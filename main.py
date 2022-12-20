#/usr/bin/env python3

import argparse
import logging
from src.release import Generate

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--access_token", dest="access_token", type=str, help="GitHub Access Token")
    parser.add_argument("-l", "--limit", dest="limit", type=int, default=10, help="Numbers of repositories to fetch")
    parser.add_argument("-f", "--force_regenerate", dest="force_regenerate", type=bool, help="Force regenerate existing files")
    
    args = parser.parse_args()
    
    access_token = args.access_token
    limit = args.limit
    force_regenerate = args.force_regenerate
    
    Generate(access_token, limit, force_regenerate)
