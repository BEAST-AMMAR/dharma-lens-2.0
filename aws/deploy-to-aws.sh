#!/bin/bash
# ============================================================================
# DEPLOY VIDHICHAKSHU TO AWS USING CLOUDFORMATION
# ============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║   VIDHICHAKSHU - AWS CLOUDFORMATION DEPLOYMENT SCRIPT      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}\n"

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo -e "${RED}✗ AWS CLI is not installed. Please install it first.${NC}"
    echo "  https://aws.amazon.com/cli/"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo -e "${RED}✗ AWS credentials not configured. Run: aws configure${NC}"
    exit 1
fi

# Get parameters
read -p "Enter stack name (default: vidhichakshu-prod): " STACK_NAME
STACK_NAME=${STACK_NAME:-vidhichakshu-prod}

read -p "Enter environment (dev/staging/prod, default: prod): " ENVIRONMENT
ENVIRONMENT=${ENVIRONMENT:-prod}

read -p "Enter EC2 Key Pair name (for SSH access): " KEY_PAIR
if [ -z "$KEY_PAIR" ]; then
    echo -e "${RED}✗ Key pair name is required${NC}"
    exit 1
fi

read -sp "Enter database password: " DB_PASSWORD
echo ""
if [ -z "$DB_PASSWORD" ]; then
    echo -e "${RED}✗ Database password is required${NC}"
    exit 1
fi

read -p "Enter instance type (t3.small/t3.medium/t3.large, default: t3.medium): " INSTANCE_TYPE
INSTANCE_TYPE=${INSTANCE_TYPE:-t3.medium}

echo -e "\n${BLUE}Stack Parameters:${NC}"
echo "  Stack Name: $STACK_NAME"
echo "  Environment: $ENVIRONMENT"
echo "  EC2 Key Pair: $KEY_PAIR"
echo "  Instance Type: $INSTANCE_TYPE"

read -p "Continue with deployment? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Deployment cancelled${NC}"
    exit 1
fi

echo -e "\n${YELLOW}Validating CloudFormation template...${NC}"
aws cloudformation validate-template --template-body file://aws/cloudformation.yaml > /dev/null
echo -e "${GREEN}✓ Template is valid${NC}"

echo -e "\n${YELLOW}Creating CloudFormation stack...${NC}"
aws cloudformation create-stack \
  --stack-name "$STACK_NAME" \
  --template-body file://aws/cloudformation.yaml \
  --parameters \
    ParameterKey=Environment,ParameterValue=$ENVIRONMENT \
    ParameterKey=KeyPairName,ParameterValue=$KEY_PAIR \
    ParameterKey=DBPassword,ParameterValue=$DB_PASSWORD \
    ParameterKey=InstanceType,ParameterValue=$INSTANCE_TYPE \
  --capabilities CAPABILITY_NAMED_IAM

echo -e "${GREEN}✓ Stack creation initiated${NC}"
echo -e "\n${YELLOW}Waiting for stack to be created (this may take 5-10 minutes)...${NC}"

aws cloudformation wait stack-create-complete --stack-name "$STACK_NAME"

echo -e "${GREEN}✓ Stack created successfully!${NC}"

echo -e "\n${BLUE}Getting stack outputs...${NC}"
OUTPUTS=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --query 'Stacks[0].Outputs')

echo -e "\n${GREEN}Stack Outputs:${NC}"
echo "$OUTPUTS" | jq -r '.[] | "\(.OutputKey): \(.OutputValue)"'

echo -e "\n${GREEN}✅ VidhiChakshu is now live on AWS!${NC}"
echo -e "${YELLOW}Note: Allow 1-2 minutes for services to fully start${NC}\n"
