# Admin Conversation Analytics E2E Test Suite

This test suite provides comprehensive end-to-end testing for the Admin Conversation Analytics feature in the UnoBot system.

## Overview

The admin conversation analytics feature allows administrators to monitor and analyze conversation performance metrics including session counts, completion rates, conversion rates, and other key business intelligence data.

## Test Coverage

The test suite verifies the following functionality:

### Core Features
- ✅ Admin dashboard loads successfully
- ✅ Conversation analytics section display
- ✅ All required metrics display correctly
- ✅ Most popular service identification
- ✅ Data consistency validation
- ✅ Responsive design across viewports
- ✅ Loading states and API integration
- ✅ UI interactions and functionality
- ✅ Complete feature verification

### Specific Metrics Tested
- **Total Sessions Count**: Number of conversation sessions
- **Completion Rate**: Percentage of completed sessions
- **PRD Conversion Rate**: Percentage of sessions that generated a PRD
- **Booking Conversion Rate**: Percentage of sessions that resulted in bookings
- **Average Session Duration**: Mean session length in minutes
- **Average Lead Score**: Mean lead quality score
- **Most Popular Service**: Service with highest recommendation count

## Test Structure

### Test File: `test_admin_conversation_analytics.py`

Contains 10 comprehensive test methods:

1. **`test_admin_dashboard_loads_successfully`**
   - Verifies admin dashboard loads without errors
   - Checks basic navigation elements
   - Validates page title and structure

2. **`test_conversation_analytics_section_display`**
   - Verifies conversation analytics section visibility
   - Checks all key metric labels are present
   - Validates analytics overview cards

3. **`test_conversation_analytics_metrics_display`**
   - Verifies numeric values are displayed
   - Checks specific metric values (sessions, rates, duration, scores)
   - Handles cases where no data exists

4. **`test_most_popular_service_display`**
   - Verifies most popular service is shown when available
   - Checks service name extraction and display
   - Handles cases with no service data

5. **`test_analytics_data_consistency`**
   - Validates data consistency (total = active + inactive experts)
   - Checks logical relationships between metrics
   - Verifies mathematical accuracy

6. **`test_analytics_section_responsive_design`**
   - Tests across multiple viewport sizes (desktop, tablet, mobile)
   - Verifies layout adapts correctly
   - Ensures all elements remain accessible

7. **`test_analytics_loading_states`**
   - Verifies loading states work correctly
   - Checks data appears after API calls complete
   - Handles timing and async behavior

8. **`test_analytics_api_integration`**
   - Verifies API calls complete successfully
   - Checks system status indicators
   - Validates backend connectivity

9. **`test_analytics_ui_interactions`**
   - Tests search functionality
   - Verifies filter buttons work
   - Checks interactive elements

10. **`test_complete_analytics_verification`**
    - Comprehensive verification of all components
    - Provides overall feature health check
    - Generates success rate metrics

### Test Runner: `run_admin_analytics_tests.py`

Provides:
- Individual test execution with detailed reporting
- Comprehensive summary of all test results
- Feature verification status
- Technical details and recommendations
- JSON report generation

## Prerequisites

Before running the tests, ensure:

1. **Backend API**: Running on `localhost:8000`
   ```bash
   cd /media/DATA/projects/autonomous-coding-uno-bot/unobot
   uv run python -m src.main
   ```

2. **Frontend**: Running on `localhost:5173`
   ```bash
   cd /media/DATA/projects/autonomous-coding-uno-bot/unobot/client
   npm run dev
   ```

3. **Test Dependencies**: Installed
   ```bash
   uv pip install -e ".[dev]"
   ```

4. **Playwright**: Browser binaries installed
   ```bash
   uv run playwright install
   ```

## Running the Tests

### Individual Test Execution
```bash
# Run specific test
uv run pytest tests/e2e/test_admin_conversation_analytics.py::test_admin_dashboard_loads_successfully -v

# Run all analytics tests
uv run pytest tests/e2e/test_admin_conversation_analytics.py -v
```

### Test Suite Runner
```bash
# Run comprehensive test suite with full reporting
python tests/e2e/run_admin_analytics_tests.py
```

### With Test Runner Script
```bash
# Make the script executable
chmod +x tests/e2e/run_admin_analytics_tests.py

# Run the test suite
./tests/e2e/run_admin_analytics_tests.py
```

## Expected Test Environment

### URLs Tested
- **Admin Dashboard**: `http://localhost:5173/admin`
- **Analytics API**: `http://localhost:5173/api/v1/admin/analytics`

### Test Data Requirements
The tests are designed to work with:
- **No test data**: Gracefully handles empty systems
- **With test data**: Validates real analytics metrics
- **Mixed scenarios**: Tests both populated and empty states

### Viewport Testing
- **Desktop**: 1280x720
- **Tablet**: 768x1024
- **Mobile**: 375x667

## Test Output

### Console Output
- ✅ Test progress and results
- 📊 Success rates and statistics
- 🔧 Debug information and recommendations
- ⚠️ Warnings for missing data (non-fatal)

### Generated Reports
- **JSON Report**: `admin_analytics_test_report.json`
- **Console Summary**: Detailed test execution summary
- **Feature Verification**: Status of each tested component

## Common Issues and Solutions

### Backend Not Running
```
ERROR: Failed to fetch analytics
```
**Solution**: Start the backend API server on localhost:8000

### Frontend Not Running
```
ERROR: Page not found
```
**Solution**: Start the frontend development server on localhost:5173

### No Test Data
```
⚠️ No conversation data found
```
**Solution**: Normal behavior. Tests handle empty systems gracefully.

### Playwright Issues
```
ERROR: Browser not found
```
**Solution**: Install Playwright browser binaries: `uv run playwright install`

### Database Issues
```
ERROR: Database connection failed
```
**Solution**: Ensure database is running and accessible

## Test Maintenance

### Adding New Tests
1. Add test method to `test_admin_conversation_analytics.py`
2. Update test patterns in `run_admin_analytics_tests.py`
3. Follow existing naming and structure patterns
4. Include comprehensive error handling

### Updating Test Data
1. Modify test data in the backend database
2. Update expected values in test assertions if needed
3. Run tests to verify changes work correctly

### Performance Optimization
1. Monitor test execution time
2. Optimize wait times and timeouts
3. Consider parallel test execution for large suites

## Integration with CI/CD

The test suite can be integrated into continuous integration pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Admin Analytics E2E Tests
  run: |
    cd /media/DATA/projects/autonomous-coding-uno-bot/unobot
    uv run python tests/e2e/run_admin_analytics_tests.py
```

## Technical Details

### Framework Stack
- **Testing**: Pytest with Playwright
- **Browser Automation**: Chromium (headless)
- **Assertion Library**: Playwright expect
- **Reporting**: JSON + Console output

### Test Patterns
- **Page Object Model**: Component-based selectors
- **Error Handling**: Graceful degradation for missing data
- **Timeout Management**: Adaptive wait times
- **Cross-browser**: Chromium-focused with responsive testing

### API Endpoints Tested
- `GET /api/v1/admin/analytics` - Complete system analytics
- `GET /api/v1/admin/analytics/conversations` - Conversation-specific metrics
- `GET /api/v1/admin/experts` - Expert management data

## Contributing

When contributing to this test suite:

1. **Follow naming conventions**: Use descriptive test method names
2. **Include documentation**: Add docstrings explaining test purpose
3. **Handle edge cases**: Account for missing data scenarios
4. **Maintain consistency**: Follow existing code style and patterns
5. **Update documentation**: Keep this README current with changes

## Support

For issues with the test suite:
1. Check the prerequisites section above
2. Review the common issues and solutions
3. Examine the generated test reports for detailed error information
4. Verify the test environment is properly configured

For feature requests or improvements:
1. Open an issue describing the enhancement
2. Include specific use cases and requirements
3. Provide examples of expected behavior