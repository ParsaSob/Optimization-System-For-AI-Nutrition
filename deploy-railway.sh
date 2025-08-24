#!/bin/bash

echo "🚀 Deploying Meal Optimization API to Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Login to Railway
echo "🔐 Logging into Railway..."
railway login

# Link project if not already linked
echo "🔗 Linking project..."
railway link

# Deploy
echo "📦 Deploying to Railway..."
railway up

echo "✅ Deployment complete!"
echo "🌐 Check your Railway dashboard for the deployment status"
echo "🔍 View logs with: railway logs"
