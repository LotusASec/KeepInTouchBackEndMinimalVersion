#!/bin/bash
# Quick API Test Script

BASE_URL="http://localhost:8000"

echo "=========================================="
echo "  Hayvan Takip API - Hızlı Test"
echo "=========================================="
echo ""

# 1. Token Al
echo "1. Token alınıyor..."
TOKEN=$(curl -s -X POST "${BASE_URL}/users/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" \
  | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "❌ Token alınamadı! Server çalışıyor mu?"
    exit 1
fi

echo "✓ Token alındı: ${TOKEN:0:20}..."
echo ""

# 2. Tüm Kullanıcıları Listele
echo "2. Tüm kullanıcılar getiriliyor..."
curl -s -X GET "${BASE_URL}/users/" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
echo ""

# 3. Tüm Hayvanları Listele
echo "3. Tüm hayvanlar getiriliyor..."
curl -s -X GET "${BASE_URL}/animals/" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
echo ""

# 4. Kullanıcı Sayısı
echo "4. İstatistikler:"
USER_COUNT=$(curl -s -X GET "${BASE_URL}/users/" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
echo "   Kullanıcı sayısı: $USER_COUNT"

ANIMAL_COUNT=$(curl -s -X GET "${BASE_URL}/animals/" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
echo "   Hayvan sayısı: $ANIMAL_COUNT"

echo ""
echo "=========================================="
echo "✓ Test tamamlandı!"
echo "=========================================="
