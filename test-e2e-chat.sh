#!/bin/bash

echo "=== MedTranslate E2E Chat Test ==="
echo ""

# 1. Create chat room
echo "[1] Creating chat room..."
RESPONSE=$(curl -s -X POST http://localhost:8001/api/chat/rooms \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "test_customer_001", "customer_language": "vi"}')

ROOM_ID=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")

echo "✓ Room created: $ROOM_ID"
echo ""

# 2. Print URLs
echo "[2] Open these URLs in separate browser windows:"
echo ""
echo "Customer Page (Vietnamese):"
echo "→ http://localhost:3001/customer/chat/$ROOM_ID?lang=vi"
echo ""
echo "Agent Console (Korean):"
echo "→ http://localhost:3001/agent/chat/$ROOM_ID"
echo ""

# 3. Test messages
echo "[3] Test message examples:"
echo ""
echo "Customer (Vietnamese):"
echo "  • Tôi bị đau đầu và sốt"
echo "  • Tôi muốn đặt lịch hẹn khám bệnh"
echo ""
echo "Agent (Korean):"
echo "  • 언제부터 증상이 시작되었나요?"
echo "  • 혈압과 체온을 측정해 주세요"
echo ""

# 4. Monitor
echo "[4] Monitor commands:"
echo ""
echo "Cache stats:"
echo "  curl http://localhost:8001/api/monitoring/cache/stats | python3 -m json.tool"
echo ""
echo "Translation provider:"
echo "  curl http://localhost:8001/api/monitoring/translation/provider | python3 -m json.tool"
echo ""
echo "Active rooms:"
echo "  curl http://localhost:8001/api/chat/rooms | python3 -m json.tool"
echo ""
echo "=== Ready for testing! ==="
