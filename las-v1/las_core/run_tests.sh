#!/bin/bash
# Run all LAS tests with proper categorization

set -e

echo "=================================="
echo "LAS Test Suite Runner"
echo "=================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}Error: pytest is not installed${NC}"
    echo "Install with: pip install -r requirements-test.txt"
    exit 1
fi

# Parse arguments
RUN_INTEGRATION=false
RUN_E2E=false
RUN_PERFORMANCE=false
COVERAGE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --integration)
            RUN_INTEGRATION=true
            shift
            ;;
        --e2e)
            RUN_E2E=true
            shift
            ;;
        --performance)
            RUN_PERFORMANCE=true
            shift
            ;;
        --coverage)
            COVERAGE=true
            shift
            ;;
        --all)
            RUN_INTEGRATION=true
            RUN_E2E=true
            RUN_PERFORMANCE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--integration] [--e2e] [--performance] [--coverage] [--all]"
            exit 1
            ;;
    esac
done

# Run unit tests
echo -e "\n${YELLOW}Running Unit Tests...${NC}"
if [ "$COVERAGE" = true ]; then
    pytest -m "not integration and not e2e and not performance" --cov=services --cov=agents --cov=routers --cov-report=term --cov-report=html -v
else
    pytest -m "not integration and not e2e and not performance" -v
fi

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Unit tests passed${NC}"
else
    echo -e "${RED}✗ Unit tests failed${NC}"
    exit 1
fi

# Run integration tests if requested
if [ "$RUN_INTEGRATION" = true ]; then
    echo -e "\n${YELLOW}Running Integration Tests...${NC}"
    pytest -m integration -v
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Integration tests passed${NC}"
    else
        echo -e "${RED}✗ Integration tests failed${NC}"
        exit 1
    fi
fi

# Run E2E tests if requested
if [ "$RUN_E2E" = true ]; then
    echo -e "\n${YELLOW}Running E2E Tests...${NC}"
    
    # Check if system is running
    if curl -s http://localhost:8000/health > /dev/null; then
        pytest -m e2e -v
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ E2E tests passed${NC}"
        else
            echo -e "${RED}✗ E2E tests failed${NC}"
            exit 1
        fi
    else
        echo -e "${RED}Error: System not running. Start with 'docker-compose up -d'${NC}"
        exit 1
    fi
fi

# Run performance tests if requested
if [ "$RUN_PERFORMANCE" = true ]; then
    echo -e "\n${YELLOW}Running Performance Tests...${NC}"
    pytest -m performance -v
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Performance tests passed${NC}"
    else
        echo -e "${RED}✗ Performance tests failed${NC}"
        exit 1
    fi
fi

echo -e "\n${GREEN}=================================="
echo "All Tests Completed Successfully!"
echo -e "==================================${NC}"

if [ "$COVERAGE" = true ]; then
    echo -e "\n${YELLOW}Coverage report generated: htmlcov/index.html${NC}"
fi
