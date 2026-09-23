# Testing Guide for TDMA Scheduler

This guide provides step-by-step instructions for testing the TDMA scheduler.

## Quick Start Testing

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run Automated Tests
```bash
python validation_tests.py
```

**Expected**: All 8 tests pass with 100% success rate

### Step 3: Run with Sample Data
```bash
python run_from_file.py sample_input.json
```

**Expected**: Complete optimization report with conflict-free schedule

## Manual Testing Scenarios

### Test 1: Basic Two-Node Test
**Purpose**: Verify nodes within range get different slots

```bash
python tdma_scheduler.py --coordinates '{"Node_A":[0.0,0.0],"Node_B":[100.0,0.0]}' --range 500.0
```

**What to check**:
- Node_A and Node_B should have different slots
- Output should say "Schedule verified conflict-free"

### Test 2: Spatial Reuse Test
**Purpose**: Verify distant nodes can share the same slot

```bash
python tdma_scheduler.py --coordinates '{"Node_01":[0.0,0.0],"Node_02":[2000.0,0.0]}' --range 500.0
```

**What to check**:
- Node_01 and Node_02 should have the same slot
- Only 1 time slot should be used

### Test 3: Hidden Terminal Test
**Purpose**: Verify 2-hop interference is handled

```bash
python tdma_scheduler.py --coordinates '{"Node_A":[0.0,0.0],"Node_B":[250.0,0.0],"Node_C":[500.0,0.0]}' --range 500.0
```

**What to check**:
- Node_A and Node_C should have different slots
- Node_B should have a different slot from both A and C

### Test 4: Small Grid Test
**Purpose**: Test with a small grid topology

```bash
python tdma_scheduler.py --coordinates '{"Node_01":[0.0,0.0],"Node_02":[300.0,0.0],"Node_03":[600.0,0.0],"Node_04":[0.0,300.0],"Node_05":[300.0,300.0],"Node_06":[600.0,300.0],"Node_07":[0.0,600.0],"Node_08":[300.0,600.0],"Node_09":[600.0,600.0]}' --range 500.0
```

**What to check**:
- Schedule should be conflict-free
- Slots should be distributed reasonably
- Spatial reuse should be visible

### Test 5: Different Radio Ranges
**Purpose**: Test scheduler flexibility

```bash
# Small range (less interference)
python run_from_file.py sample_input.json --range 400

# Large range (more interference)
python run_from_file.py sample_input.json --range 600
```

**What to check**:
- Smaller range should use fewer slots
- Larger range should use more slots
- Both should be conflict-free

## Testing Methodology

### 1. Correctness Testing
Run the automated test suite:
```bash
python validation_tests.py
```

This tests:
- ✅ Basic functionality
- ✅ Direct interference avoidance
- ✅ Hidden terminal problem
- ✅ Spatial reuse
- ✅ Isolated nodes
- ✅ 16-node specification
- ✅ Slot efficiency
- ✅ Graph structure

### 2. Performance Testing
Test with different network sizes:

**Small Network (4 nodes)**:
```bash
python tdma_scheduler.py --coordinates '{"Node_01":[0.0,0.0],"Node_02":[300.0,0.0],"Node_03":[600.0,0.0],"Node_04":[900.0,0.0]}' --range 500.0
```

**Medium Network (9 nodes)**:
```bash
python tdma_scheduler.py --coordinates '{"Node_01":[0.0,0.0],"Node_02":[300.0,0.0],"Node_03":[600.0,0.0],"Node_04":[0.0,300.0],"Node_05":[300.0,300.0],"Node_06":[600.0,300.0],"Node_07":[0.0,600.0],"Node_08":[300.0,600.0],"Node_09":[600.0,600.0]}' --range 500.0
```

**Large Network (16 nodes)**:
```bash
python run_from_file.py sample_input.json
```

### 3. Edge Case Testing

**Single Node**:
```bash
python tdma_scheduler.py --coordinates '{"Node_01":[0.0,0.0]}' --range 500.0
```
Expected: 1 slot, conflict-free

**Many Isolated Nodes**:
```bash
python tdma_scheduler.py --coordinates '{"Node_01":[0.0,0.0],"Node_02":[2000.0,0.0],"Node_03":[4000.0,0.0]}' --range 500.0
```
Expected: All nodes share 1 slot

**Dense Network**:
```bash
python tdma_scheduler.py --coordinates '{"Node_01":[0.0,0.0],"Node_02":[100.0,0.0],"Node_03":[200.0,0.0],"Node_04":[300.0,0.0]}' --range 500.0
```
Expected: Many slots due to high interference

## Interpreting Results

### Success Indicators
- ✅ "Schedule verified conflict-free" in output
- ✅ Reasonable number of slots for the topology
- ✅ Spatial reuse visible (distant nodes sharing slots)
- ✅ All automated tests pass

### Failure Indicators
- ❌ "WARNING: Schedule contains conflicts!"
- ❌ Excessive number of slots (inefficient)
- ❌ Nodes within range sharing slots (wrong)
- ❌ Automated test failures

## Common Issues and Solutions

### Issue: "Module not found" error
**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: Invalid JSON format
**Solution**: Ensure coordinates are valid JSON
```bash
# Correct format
python tdma_scheduler.py --coordinates '{"Node_01":[0.0,0.0]}'

# Incorrect format (missing quotes)
python tdma_scheduler.py --coordinates '{Node_01:[0.0,0.0]}'
```

### Issue: Too many slots used
**Solution**: This may be normal for dense networks. Check if:
- Radio range is too large
- Network topology is very dense
- Schedule is still conflict-free

### Issue: Unicode encoding errors
**Solution**: Use the provided scripts which handle encoding correctly

## Advanced Testing

### Custom Test Cases
Create your own test JSON files:

```json
{
    "Node_01": [0.0, 0.0],
    "Node_02": [350.0, 0.0],
    "Node_03": [700.0, 0.0]
}
```

Save as `custom_test.json` and run:
```bash
python run_from_file.py custom_test.json
```

### Algorithm Comparison
Test with different parameters to see algorithm behavior:

```bash
# Compare different radio ranges
for range in 300 400 500 600; do
    echo "Testing with range $range"
    python run_from_file.py sample_input.json --range $range
done
```

### Stress Testing
Test with larger networks (modify sample_input.json to add more nodes):
```bash
# Add nodes up to Node_25, Node_36, etc.
python run_from_file.py large_network.json
```

## Verification Checklist

Before submission, verify:

- [ ] All 8 automated tests pass
- [ ] 16-node specification test works correctly
- [ ] Schedule is always conflict-free
- [ ] Spatial reuse is demonstrated
- [ ] Different radio ranges produce expected results
- [ ] Edge cases (single node, isolated nodes) work
- [ ] Output format matches specification
- [ ] Documentation is clear and complete

## Getting Help

If tests fail:
1. Check Python version (requires 3.6+)
2. Verify NetworkX installation
3. Check input JSON format
4. Review error messages carefully
5. Consult VERIFICATION.md for detailed debugging

## Next Steps After Testing

Once testing is complete:
1. Document any interesting findings
2. Note any edge cases you discovered
3. Prepare test results for presentation
4. Consider additional optimizations if needed
