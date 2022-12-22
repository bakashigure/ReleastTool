#/usr/bin/env python3

import argparse
import logging
from src.release import Generate

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--access_token", dest="access_token", type=str, help="GitHub Access Token")
    parser.add_argument("-l", "--limit", dest="limit", type=int, default=8, help="Numbers of repositories to fetch, default to 8, max to 15")
    parser.add_argument("-f", "--force_regenerate", dest="force_regenerate", type=bool, help="Force regenerate existing files")
    parser.add_argument("-t", "--target_tag", dest="target_tag", type=str, default=None, help="Target tag to generate")
    
    args = parser.parse_args()
    
    access_token = args.access_token
    limit = args.limit
    force_regenerate = args.force_regenerate
    target_tag = args.target_tag
    
    if not access_token:
        logging.error("Missing arguments")
        exit(1)
    
    if limit > 15:
        logging.error("Limit should be less than 15")
        exit(1)
    
    Generate(access_token, limit, force_regenerate, target_tag)
