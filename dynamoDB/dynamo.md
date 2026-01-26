aws dynamodb create-table `
  --table-name Players `
  --attribute-definitions `
    AttributeName=playerId,AttributeType=S `
    AttributeName=status,AttributeType=S `
    AttributeName=createdAt,AttributeType=N `
    AttributeName=roomId,AttributeType=S `
    AttributeName=connectionId,AttributeType=S `
  --key-schema `
    AttributeName=playerId,KeyType=HASH `
  --billing-mode PROVISIONED `
  --provisioned-throughput ReadCapacityUnits=1,WriteCapacityUnits=1 `
  --global-secondary-indexes '[
    {
      "IndexName": "GSI_Status",
      "KeySchema": [
        {"AttributeName": "status", "KeyType": "HASH"},
        {"AttributeName": "createdAt", "KeyType": "RANGE"}
      ],
      "Projection": {"ProjectionType": "ALL"},
      "ProvisionedThroughput": {
        "ReadCapacityUnits": 1,
        "WriteCapacityUnits": 1
      }
    },
    {
      "IndexName": "GSI_Room",
      "KeySchema": [
        {"AttributeName": "roomId", "KeyType": "HASH"},
        {"AttributeName": "connectionId", "KeyType": "RANGE"}
      ],
      "Projection": {"ProjectionType": "ALL"},
      "ProvisionedThroughput": {
        "ReadCapacityUnits": 1,
        "WriteCapacityUnits": 1
      }
    }
  ]'


aws dynamodb update-time-to-live `
  --table-name Players `
  --time-to-live-specification `
    Enabled=true,AttributeName=ttl

aws dynamodb create-table `
  --table-name Games `
  --attribute-definitions `
    AttributeName=roomId,AttributeType=S `
  --key-schema `
    AttributeName=roomId,KeyType=HASH `
  --billing-mode PROVISIONED `
  --provisioned-throughput ReadCapacityUnits=1,WriteCapacityUnits=1


aws dynamodb update-time-to-live `
  --table-name Games `
  --time-to-live-specification "Enabled=true, AttributeName=ttl"