#!/bin/bash

# SSL Certificate Setup Script
# This script helps generate self-signed certificates for development
# or sets up Let's Encrypt for production

set -e

echo "🔒 SSL Certificate Setup"
echo "======================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SSL_DIR="ssl"
CERT_FILE="$SSL_DIR/cert.pem"
KEY_FILE="$SSL_DIR/key.pem"

# Create SSL directory
mkdir -p $SSL_DIR

echo "Select certificate type:"
echo "1. Self-signed (Development)"
echo "2. Let's Encrypt (Production)"
echo "3. Custom certificates"
echo ""
read -p "Enter choice [1-3]: " choice

case $choice in
    1)
        echo -e "${YELLOW}Generating self-signed certificate...${NC}"
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout $KEY_FILE \
            -out $CERT_FILE \
            -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
        
        echo -e "${GREEN}✓ Self-signed certificate generated${NC}"
        echo "  Certificate: $CERT_FILE"
        echo "  Private Key: $KEY_FILE"
        echo ""
        echo -e "${YELLOW}Note: Browsers will show a security warning with self-signed certs${NC}"
        ;;
    
    2)
        echo -e "${YELLOW}Setting up Let's Encrypt...${NC}"
        echo ""
        echo "Requirements:"
        echo "- Domain name pointing to your server"
        echo "- Ports 80 and 443 open"
        echo "- certbot installed"
        echo ""
        
        read -p "Enter your domain: " domain
        
        if ! command -v certbot &> /dev/null; then
            echo -e "${RED}certbot is not installed. Installing...${NC}"
            if command -v apt &> /dev/null; then
                sudo apt update && sudo apt install -y certbot
            elif command -v yum &> /dev/null; then
                sudo yum install -y certbot
            else
                echo -e "${RED}Please install certbot manually${NC}"
                exit 1
            fi
        fi
        
        echo -e "${YELLOW}Requesting certificate from Let's Encrypt...${NC}"
        sudo certbot certonly --standalone -d $domain -d www.$domain
        
        if [ -f "/etc/letsencrypt/live/$domain/fullchain.pem" ]; then
            echo -e "${GREEN}✓ Certificate obtained successfully${NC}"
            echo ""
            echo "To auto-renew, add to crontab:"
            echo "0 3 * * * certbot renew --quiet"
            echo ""
            echo "Copy certificates to ssl directory:"
            echo "  sudo cp /etc/letsencrypt/live/$domain/fullchain.pem $CERT_FILE"
            echo "  sudo cp /etc/letsencrypt/live/$domain/privkey.pem $KEY_FILE"
        else
            echo -e "${RED}Failed to obtain certificate${NC}"
            exit 1
        fi
        ;;
    
    3)
        echo -e "${YELLOW}Using custom certificates${NC}"
        echo ""
        echo "Place your certificate files in the $SSL_DIR directory:"
        echo "  - cert.pem (certificate)"
        echo "  - key.pem (private key)"
        echo ""
        read -p "Press Enter when ready..."
        
        if [ -f "$CERT_FILE" ] && [ -f "$KEY_FILE" ]; then
            echo -e "${GREEN}✓ Custom certificates found${NC}"
        else
            echo -e "${RED}✗ Certificate files not found${NC}"
            exit 1
        fi
        ;;
    
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}SSL setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Update nginx configuration with your domain"
echo "2. Restart Docker containers: ./scripts/docker-prod.sh restart"
echo "3. Test HTTPS access"
