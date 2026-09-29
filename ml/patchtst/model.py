"""
ml/patchtst/model.py — Enhanced PatchTST PyTorch Architecture.
Includes Reversible Instance Normalization (RevIN), Channel Independence,
and multi-layer projection head for high-accuracy traffic forecasting.
"""
import torch
import torch.nn as nn


class RevIN(nn.Module):
    """
    Reversible Instance Normalization for Non-Stationary Time-Series.
    Normalizes inputs per-instance to zero mean and unit variance,
    and reverses the normalization on output forecasts.
    """
    def __init__(self, num_features: int, eps=1e-5, affine=True):
        super().__init__()
        self.num_features = num_features
        self.eps = eps
        self.affine = affine
        if self.affine:
            self.affine_weight = nn.Parameter(torch.ones(num_features))
            self.affine_bias = nn.Parameter(torch.zeros(num_features))

    def forward(self, x, mode: str):
        if mode == 'norm':
            self.mean = torch.mean(x, dim=1, keepdim=True).detach()
            self.stdev = torch.sqrt(torch.var(x, dim=1, keepdim=True, unbiased=False) + self.eps).detach()
            x = (x - self.mean) / self.stdev
            if self.affine:
                x = x * self.affine_weight + self.affine_bias
            return x
        elif mode == 'denorm':
            if self.affine:
                x = (x - self.affine_bias) / (self.affine_weight + self.eps)
            x = x * self.stdev + self.mean
            return x
        else:
            raise NotImplementedError(f"RevIN mode '{mode}' is not supported.")


class PatchTST(nn.Module):
    def __init__(self, config, num_features):
        super().__init__()
        self.seq_len = config.context_length
        self.pred_len = config.forecast_horizon
        self.patch_len = config.patch_length
        self.stride = config.patch_stride
        self.num_features = num_features
        self.d_model = config.d_model

        # Reversible Instance Normalization
        self.revin = RevIN(num_features, affine=True)

        # Calculate number of patches
        self.num_patches = int((self.seq_len - self.patch_len) / self.stride) + 2

        # Linear patching projection
        self.patch_proj = nn.Linear(self.patch_len, self.d_model)

        # Positional encoding
        self.positional_encoding = nn.Parameter(torch.randn(1, self.num_patches, self.d_model) * 0.02)

        # Transformer Encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=self.d_model,
            nhead=config.n_heads,
            dim_feedforward=self.d_model * 4,
            dropout=config.dropout,
            batch_first=True,
            activation="gelu"
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=config.n_encoder_layers)

        # Enhanced MLP head with GELU
        self.head = nn.Sequential(
            nn.Linear(self.num_patches * self.d_model, self.d_model),
            nn.GELU(),
            nn.Dropout(config.dropout),
            nn.Linear(self.d_model, self.pred_len)
        )

    def forward(self, x):
        # x: [Batch, SeqLen, Features]
        B, L, M = x.shape

        # 1. Reversible Instance Normalization (removes non-stationary drift)
        x = self.revin(x, 'norm')

        # 2. Unfold into patches: [Batch, Features, NumPatches, PatchLen]
        pad_len = self.patch_len - self.stride
        x = torch.cat([x[:, :pad_len, :], x], dim=1) # [B, L+pad_len, M]
        x = x.unfold(1, self.patch_len, self.stride) # [B, NumPatches, M, PatchLen]

        # 3. Channel Independence: treat features as independent batch elements
        x = x.permute(0, 2, 1, 3).contiguous().view(B * M, self.num_patches, self.patch_len)
        x = self.patch_proj(x)
        x = x + self.positional_encoding
        x = self.transformer(x)

        # 4. Prediction head
        x = x.view(B * M, -1)
        x = self.head(x) # [B*M, pred_len]

        # 5. Reshape back to [Batch, pred_len, Features]
        x = x.view(B, M, self.pred_len).permute(0, 2, 1)

        # 6. Reverse Instance Normalization (restores physical scale)
        x = self.revin(x, 'denorm')

        return x
