# 📊 Code Coverage Report - AI Service

**Branch:** ai-service-dev
**Commit:** [\`3627f52\`](https://github.com/openchlai/ai/commit/3627f529a410cc39226159e3783bf04b6eccafa5)
**Generated:** 2026-02-02 09:25:39 UTC
**Python Version:** 3.12
**Workflow:** [\`21584183237\`](https://github.com/openchlai/ai/actions/runs/21584183237)

## 🎯 Coverage Summary

![Coverage](https://img.shields.io/badge/Coverage-83%25-brightgreen)

**Coverage:** 83%

## 📈 Detailed Coverage Report

```
Name                                            Stmts   Miss  Cover   Missing
-----------------------------------------------------------------------------
app/__init__.py                                     1      0   100%
app/api/__init__.py                                 0      0   100%
app/api/agent_feedback_routes.py                   93      0   100%
app/api/audio_routes.py                           282     17    94%   56, 133, 379, 480, 482, 490, 495, 499-500, 518-538, 595
app/api/call_session_routes.py                    224     14    94%   14-15, 210-237, 403, 422
app/api/classifier_route.py                       105      0   100%
app/api/health_routes.py                          113      2    98%   48-49
app/api/models.py                                  57      0   100%
app/api/ner_routes.py                              89      0   100%
app/api/notification_routes.py                     93      3    97%   249-251
app/api/processing_mode_routes.py                  97      1    99%   174
app/api/qa_route.py                                85      2    98%   90, 161
app/api/summarizer_routes.py                       80      0   100%
app/api/translator_routes.py                       77      0   100%
app/api/whisper_routes.py                         109      1    99%   74
app/celery_app.py                                  20      6    70%   12-25
app/config/__init__.py                              0      0   100%
app/config/settings.py                            173      0   100%
app/core/__init__.py                                0      0   100%
app/core/celery_monitor.py                         61      0   100%
app/core/enhanced_processing_manager.py            75      0   100%
app/core/insights_service.py                       70      0   100%
app/core/metrics.py                                68      0   100%
app/core/notification_manager.py                  159     11    93%   113-114, 223-225, 258-259, 282-284, 288
app/core/processing_modes.py                       93      2    98%   149-150
app/core/processing_strategy_manager.py           137     20    85%   150, 160, 195-210, 299-300, 304, 358-362, 366-368
app/core/resource_manager.py                      118      0   100%
app/core/streaming.py                             106      3    97%   246-248
app/core/text_chunker.py                          156     15    90%   70-72, 77-79, 86-87, 98, 159-172
app/db/models.py                                   18      0   100%
app/db/repositories/feedback_repository.py         77      0   100%
app/db/session.py                                  22      0   100%
app/main.py                                       135     26    81%   64-65, 75-77, 88-89, 95, 110-113, 127-128, 185, 252-253, 281-302
app/model_scripts/__init__.py                       7      0   100%
app/model_scripts/audio_processing.py               0      0   100%
app/model_scripts/classifier_model.py             302     32    89%   20-28, 31-47, 101-102, 262-275, 505
app/model_scripts/model_loader.py                 249     81    67%   16-18, 24-26, 32-34, 40-42, 48-50, 56-58, 64-66, 89-125, 177, 195, 202-203, 223-224, 260-261, 270-274, 303-307, 319-323, 331-344, 395, 410, 421
app/model_scripts/ner_model.py                    161     36    78%   14-16, 83-103, 120-123, 136, 163-165, 193-197, 201, 224-226, 260-261
app/model_scripts/qa_model.py                     155     54    65%   47-54, 60-66, 94-127, 134-158, 226-228, 259-260
app/model_scripts/summarizer_model.py             163      4    98%   213, 240-241, 282
app/model_scripts/translator_model.py             178     48    73%   53-57, 60-61, 70-71, 73-74, 117-122, 158-160, 164-201, 219-222, 241, 253-256, 293, 307-308
app/model_scripts/whisper_model.py                254    117    54%   69, 77-78, 128-171, 183-211, 229-234, 248, 267-320, 344-363, 369-371, 409-484
app/models/__init__.py                              2      0   100%
app/models/notification_types.py                   63      0   100%
app/security/__init__.py                            2      0   100%
app/security/pii_log_scanner.py                   359     20    94%   40-41, 49-50, 53-59, 270, 355, 432-446, 536, 991
app/security/pii_logging_filter.py                132     20    85%   357-415
app/security/pii_monitor.py                       184      3    98%   23-24, 487
app/services/enhanced_notification_service.py     328      4    99%   308, 524-525, 849
app/streaming/__init__.py                           3      0   100%
app/streaming/audio_buffer.py                      36      0   100%
app/streaming/call_session_manager.py             551    278    50%   45-47, 65, 71-78, 90-93, 121, 167-169, 220-221, 229, 237-239, 287-288, 313, 319-323, 335-336, 345-349, 353-354, 356-357, 360, 385-387, 391-478, 524-526, 530-637, 641-666, 670-700, 704-763, 773-788, 792-870, 898-899, 921-923, 956, 960-961, 994-996, 1004, 1016-1046
app/streaming/progressive_processor.py            247     10    96%   16-18, 79, 125, 372-374, 386-387
app/streaming/tcp_server.py                       111      4    96%   131-132, 136-137
app/streaming/websocket_server.py                  57      0   100%
app/tasks/__init__.py                               0      0   100%
app/tasks/audio_tasks.py                          510    450    12%   28-167, 197-198, 209-418, 450-473, 513-1035, 1059-1087, 1103, 1109-1143, 1197-1305, 1309-1311
app/tasks/health_tasks.py                          11      0   100%
app/tasks/model_tasks.py                          300     20    93%   34-59, 67, 559
app/utils/__init__.py                               2      0   100%
app/utils/audio_utils.py                            0      0   100%
app/utils/mode_detector.py                         16      0   100%
app/utils/scp_audio_downloader.py                 232     22    91%   45, 51, 124-126, 138-140, 239-241, 353, 360-361, 385, 438, 546-555
app/utils/text_utils.py                           268     20    93%   90-91, 158-169, 186, 241-242, 302-316, 357-358, 560
-----------------------------------------------------------------------------
TOTAL                                            7876   1346    83%
```

---
*Report generated automatically by GitHub Actions*
*Access this report at: [COVERAGE.md](https://github.com/openchlai/ai/blob/ai-service-dev/ai_service/COVERAGE.md)*
