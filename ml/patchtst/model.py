"""
ml/patchtst/model.py — PatchTST PyTorch Architecture.
"""
import torch
import torch.nn as nn

class PatchTST(nn.Module):
    def __init__(self, config, num_features):
        super().__init__()
        self.seq_len = config.context_length
        self.pred_len = config.forecast_horizon
        self.patch_len = config.patch_length
        self.stride = config.patch_stride
        self.num_features = num_features
        
        self.d_model = config.d_model
        
        # Calculate number of patches
        self.num_patches = int((self.seq_len - self.patch_len) / self.stride) + 2
        
        # Linear patching projection
        self.patch_proj = nn.Linear(self.patch_len, self.d_model)
        
        # Positional encoding
        self.positional_encoding = nn.Parameter(torch.randn(1, self.num_patches, self.d_model))
        
        # Transformer Encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=self.d_model,
            nhead=config.n_heads,
            dim_feedforward=self.d_model * 4,
            dropout=config.dropout,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=config.n_encoder_layers)
        
        # Flatten and project to prediction horizon
        self.head = nn.Linear(self.num_patches * self.d_model, self.pred_len)
        
    def forward(self, x):
        # x: [Batch, SeqLen, Features]
        B, L, M = x.shape
        
        # Unfold into patches: [Batch, Features, NumPatches, PatchLen]
        # To do this cleanly, we process each feature independently (Channel Independence)
        
        # Pad sequence to ensure patches fit perfectly
        pad_len = self.patch_len - self.stride
        x = torch.cat([x[:, :pad_len, :], x], dim=1) # [B, L+pad_len, M]
        
        # Create patches
        x = x.unfold(1, self.patch_len, self.stride) # [B, NumPatches, M, PatchLen]
        
        # Reshape for channel independence: treat features as batch
        # [B * M, NumPatches, PatchLen]
        x = x.permute(0, 2, 1, 3).contiguous().view(B * M, self.num_patches, self.patch_len)
        
        # Project patches
        x = self.patch_proj(x) # [B*M, NumPatches, d_model]
        
        # Add positional encoding
        x = x + self.positional_encoding
        
        # Transformer
        x = self.transformer(x) # [B*M, NumPatches, d_model]
        
        # Flatten patches
        x = x.view(B * M, -1) # [B*M, NumPatches * d_model]
        
        # Prediction head
        x = self.head(x) # [B*M, pred_len]
        
        # Reshape back to [Batch, pred_len, Features]
        x = x.view(B, M, self.pred_len).permute(0, 2, 1)
        
        return x
