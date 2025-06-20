for i in {1..7}; do
  curl -X POST http://localhost:8001/api/orders/ \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE3NTA0MzgxMDl9.UJvwFd_dSu70KJOEQcu7wQV11WFt35wR9m2LpmYfC-A" \
    -H "Content-Type: application/json" \
    -d '{"items":[{"product_id":1,"quantity":1}]}'
done