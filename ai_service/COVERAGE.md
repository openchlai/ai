# 📊 Code Coverage Report - AI Service

**Branch:** 471/merge
**Commit:** [\`f36c522\`](https://github.com/openchlai/ai/commit/f36c522c305ede35795cd58c483a21e3507c53af)
**Generated:** 2026-01-23 09:12:35 UTC
**Python Version:** 3.12
**Workflow:** [\`21280617112\`](https://github.com/openchlai/ai/actions/runs/21280617112)

## 🎯 Coverage Summary

![Coverage](https://img.shields.io/badge/Coverage-76%25-yellow)

**Coverage:** 76%

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
app/celery_app.py                                  10      0   100%
app/config/__init__.py                              0      0   100%
app/config/settings.py                            172      0   100%
app/core/__init__.py                                0      0   100%
app/core/celery_monitor.py                         61     32    48%   26-89
app/core/enhanced_processing_manager.py            75      0   100%
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
app/main.py                                       130     60    54%   44-119, 176, 243-244, 272-293
app/model_scripts/__init__.py                       7      0   100%
app/model_scripts/audio_processing.py               0      0   100%
app/model_scripts/classifier_model.py             302    182    40%   20-28, 31-47, 90-91, 95-119, 128-167, 180, 183, 186-190, 207, 220-221, 274-282, 311-337, 345, 351-431, 455-462, 466, 490-505, 509-520, 535-552, 558
app/model_scripts/model_loader.py                 249    109    56%   16-18, 24-26, 32-34, 40-42, 48-50, 56-58, 64-66, 89-125, 177, 195, 202-203, 209-212, 223-224, 260-261, 267-279, 292-293, 298-344, 395, 410, 421
app/model_scripts/ner_model.py                    161     65    60%   14-16, 44-45, 54-70, 83-103, 120-123, 129-132, 136, 143, 163-165, 180-197, 201, 217-226, 253, 261, 272
app/model_scripts/qa_model.py                     155     96    38%   47-54, 60-66, 94-127, 140-158, 174-228, 232-279, 287-289
app/model_scripts/summarizer_model.py             163    100    39%   39-63, 87, 100-105, 127-129, 139-201, 205-213, 218-243, 248, 265-282, 286-298, 302-317, 341-353
app/model_scripts/translator_model.py             178     85    52%   53-57, 60-61, 73-74, 117-122, 158-160, 164-201, 207-225, 229-258, 263, 277-293, 297-308
app/model_scripts/whisper_model.py                254     82    68%   77-78, 128-171, 196-204, 231, 267-320, 344-363, 407, 410-411, 418, 442-464, 474-475, 482-484
app/models/__init__.py                              0      0   100%
app/models/model_loader.py                         12     12     0%   2-18
app/models/notification_types.py                   61      0   100%
app/services/enhanced_notification_service.py     328      4    99%   308, 524-525, 848
app/services/insights_service.py                   84      0   100%
app/streaming/__init__.py                           3      0   100%
app/streaming/audio_buffer.py                      36      0   100%
app/streaming/call_session_manager.py             550    277    50%   45-47, 65, 71-78, 90-93, 121, 167-169, 220-221, 237-239, 280-284, 287-288, 319-323, 335-336, 345-349, 353-354, 356-357, 360, 385-387, 391-478, 524-526, 530-636, 640-665, 669-699, 703-762, 772-787, 791-869, 920-922, 955, 959-960, 993-995, 1003, 1015-1045
app/streaming/progressive_processor.py            247     10    96%   16-18, 79, 125, 372-374, 386-387
app/streaming/tcp_server.py                       111      4    96%   131-132, 136-137
app/streaming/websocket_server.py                  57      0   100%
app/tasks/__init__.py                               0      0   100%
app/tasks/audio_tasks.py                          473    414    12%   28-167, 197-198, 209-379, 411-434, 474-936, 960-988, 1004, 1010-1044, 1098-1206, 1210-1212
app/tasks/health_tasks.py                          11      0   100%
app/tasks/model_tasks.py                          300     20    93%   34-59, 67, 559
app/utils/__init__.py                               2      0   100%
app/utils/audio_utils.py                            0      0   100%
app/utils/mode_detector.py                         16      0   100%
app/utils/scp_audio_downloader.py                 232     22    91%   45, 51, 124-126, 138-140, 239-241, 353, 360-361, 385, 438, 546-555
app/utils/text_utils.py                           268     20    93%   90-91, 158-169, 186, 241-242, 302-316, 357-358, 560
-----------------------------------------------------------------------------
TOTAL                                            7167   1685    76%
```

---
*Report generated automatically by GitHub Actions*
*Access this report at: [COVERAGE.md](https://github.com/openchlai/ai/blob/471/merge/ai_service/COVERAGE.md)*
