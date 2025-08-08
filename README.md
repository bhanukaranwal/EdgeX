# EdgeX - Automated Options Trading Bot for NSE Nifty 50 & Sensex

EdgeX is a professional-grade trading automation platform featuring multi-strategy options trading, AI-based analytics, and Zerodha PyKiteConnect integration. Designed for modularity, extensibility, and institution-level risk management.

## Features
- Advanced options strategies (Supertrend, Greeks-based, Straddle/Strangle)
- Live trading and backtesting
- Plug-and-play strategy and risk modules
- Real-time analytics & AI/ML modules
- Secure broker connectivity (Zerodha)
- RESTful API for dashboard & controls
- Full automated deployment support

## Getting Started

1. Clone the repo  
2. Install dependencies  
   `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and configure your keys
4. Edit configs in `config/`
5. Start the bot  
   `python -m edgeX.main`
6. UI server:  
   `sh scripts/start_ui.sh`

## Contribution

See [docs/developer_handbook.md](docs/developer_handbook.md).
Pull requests and feedback welcome!

## License  
See LICENSE.
