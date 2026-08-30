"""
ml/patchtst/training.py — Training pipeline for PatchTST.
"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import json
import datetime
from pathlib import Path
import numpy as np

from ml.patchtst.config import PatchTSTConfig
from ml.patchtst.dataset import TrafficDataset, load_data_from_mongo
from ml.patchtst.model import PatchTST

def train_patchtst(db):
    """
    Main training function triggered by Admin.
    """
    config = PatchTSTConfig()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training PatchTST on {device}")
    
    # 1. Load Data
    df = load_data_from_mongo(db)
    num_features = df.shape[1]
    
    # Simple split 80/20
    split_idx = int(len(df) * 0.8)
    train_df = df.iloc[:split_idx]
    test_df = df.iloc[split_idx:]
    
    train_dataset = TrafficDataset(train_df, config, is_train=True)
    test_dataset = TrafficDataset(test_df, config, is_train=False, scaler=train_dataset.scaler)
    
    train_loader = DataLoader(train_dataset, batch_size=config.batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=config.batch_size, shuffle=False)
    
    # 2. Initialize Model
    model = PatchTST(config, num_features).to(device)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=config.learning_rate)
    
    # 3. Training Loop
    best_val_loss = float("inf")
    patience_counter = 0
    
    for epoch in range(config.epochs):
        model.train()
        train_loss = 0.0
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            
            optimizer.zero_grad()
            out = model(x)
            loss = criterion(out, y)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item() * x.size(0)
            
        train_loss /= len(train_loader.dataset)
        
        # Validation
        model.eval()
        val_loss = 0.0
        val_mae = 0.0
        with torch.no_grad():
            for x, y in test_loader:
                x, y = x.to(device), y.to(device)
                out = model(x)
                loss = criterion(out, y)
                val_loss += loss.item() * x.size(0)
                val_mae += torch.abs(out - y).mean().item() * x.size(0)
                
        val_loss /= len(test_loader.dataset)
        val_mae /= len(test_loader.dataset)
        
        print(f"Epoch {epoch+1}/{config.epochs} - Train Loss: {train_loss:.4f} - Val Loss (MSE): {val_loss:.4f} - Val MAE: {val_mae:.4f}")
        
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            # Save best model
            torch.save(model.state_dict(), config.model_path)
            
            # Unscale metrics for reporting
            std_mean = float(np.mean(train_dataset.std))
            actual_mae = float(val_mae * std_mean)
            actual_rmse = float(np.sqrt(val_loss) * std_mean)
            actual_mape = float(actual_mae / (float(np.mean(train_dataset.mean)) + 1e-5))
            
            # Save metrics
            metrics = {
                "status": "success",
                "timestamp": datetime.datetime.now().isoformat(),
                "mae": round(actual_mae, 4),
                "rmse": round(actual_rmse, 4),
                "mape": round(actual_mape, 4),
                "val_loss_scaled": round(float(val_loss), 4)
            }
            with open(config.metrics_path, "w") as f:
                json.dump(metrics, f, indent=2)
        else:
            patience_counter += 1
            if patience_counter >= config.patience:
                print(f"Early stopping at epoch {epoch+1}")
                break
                
    return metrics
