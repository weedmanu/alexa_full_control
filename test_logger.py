#!/usr/bin/env python3
from utils.logger import get_logger

logger = get_logger()
print('Test direct:')
logger.log('AUTH', 'Test AUTH')

print()
print('Test avec bind:')
bound_logger = logger.bind(command='TestCommand')
bound_logger.log('AUTH', 'Test AUTH bound')