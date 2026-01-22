# 📊 Code Coverage Report - AI Service

**Branch:** justphyl
**Commit:** [\`fdc3997\`](https://github.com/openchlai/ai/commit/fdc39978ab1ac50eb22fb5413ea67923d2627373)
**Generated:** 2026-01-22 08:13:21 UTC
**Python Version:** 3.12
**Workflow:** [\`21240796750\`](https://github.com/openchlai/ai/actions/runs/21240796750)

## 🎯 Coverage Summary

![Coverage](https://img.shields.io/badge/Coverage-45%25-orange)

**Coverage:** 56%

## 📈 Detailed Coverage Report

```
Name                                            Stmts   Miss  Cover   Missing
-----------------------------------------------------------------------------
app/__init__.py                                     1      0   100%
app/api/__init__.py                                 0      0   100%
app/api/agent_feedback_routes.py                   93     49    47%   30-33, 77-117, 133-152, 167-183, 192-217
app/api/audio_routes.py                           276    192    30%   43, 110, 115, 148-150, 189, 197-199, 204-229, 234-239, 244-303, 312-340, 355-553, 571-667
app/api/call_session_routes.py                    224     85    62%   14-15, 117, 130-134, 145, 170-174, 182, 193, 210-237, 247, 251, 262, 273, 281-291, 296-306, 313-335, 340-357, 362-391, 403-411, 422-432
app/api/classifier_route.py                       104     30    71%   81-82, 109-111, 117-172, 186-200, 209-216
app/api/health_routes.py                          113     56    50%   48-49, 112-154, 175, 182-251, 274-296
app/api/ner_routes.py                              88     31    65%   64-65, 94-96, 113-167, 187-203
app/api/notification_routes.py                     93     65    30%   30-38, 43-73, 78-97, 102-127, 132-141, 146-202, 207-251
app/api/processing_mode_routes.py                  95     65    32%   32-41, 46-59, 64-92, 97-120, 125-144, 149-186, 190-196
app/api/qa_route.py                                83     30    64%   63-65, 71, 89-91, 97-146, 151-159, 164-176
app/api/summarizer_routes.py                       80     27    66%   57-58, 79-81, 87-135, 150-157
app/api/translator_routes.py                       77     30    61%   50-51, 76-78, 84-132, 150-166, 177-189
app/api/whisper_routes.py                         109     44    60%   66-67, 74, 116-155, 163-213, 227-241, 261-276
app/celery_app.py                                  10      1    90%   8
app/config/__init__.py                              0      0   100%
app/config/settings.py                            172     31    82%   266, 696-709, 720, 731-733, 742, 792-798, 847, 862-875
app/core/__init__.py                                0      0   100%
app/core/celery_monitor.py                         61     42    31%   21-93, 97, 106, 114
app/core/enhanced_processing_manager.py            75     10    87%   62-63, 69-71, 116-122
app/core/metrics.py                                68     36    47%   160-176, 188-201, 210, 215, 220, 225, 230, 235
app/core/notification_manager.py                  159    121    24%   43-46, 62-64, 77-114, 118-119, 123-124, 128-132, 136-142, 161-182, 186-202, 208-271, 275-284, 288, 303-309
app/core/processing_modes.py                       93     26    72%   106, 110, 116-150, 154
app/core/processing_strategy_manager.py           137    103    25%   60-93, 116-143, 149-153, 159-163, 168, 173, 183-210, 220-264, 276-287, 299-300, 304, 334-368
app/core/resource_manager.py                      118     25    79%   88-89, 134-135, 150-151, 166-167, 197, 201-206, 210-228, 235-239
app/core/streaming.py                             106     80    25%   22-29, 33-40, 44, 56-86, 96, 118, 141-143, 160, 175, 193-261, 265-283, 287-294
app/core/text_chunker.py                          156     26    83%   70-72, 77-79, 86-90, 98, 158-182, 290
app/db/models.py                                   18      1    94%   34
app/db/repositories/feedback_repository.py         77     61    21%   42-67, 90-122, 141-151, 170-213
app/db/session.py                                  22     11    50%   27-31, 37-44
app/main.py                                       129     76    41%   41-116, 173, 178-181, 190, 226-247, 262-265, 269-290
app/model_scripts/__init__.py                       7      0   100%
app/model_scripts/audio_processing.py               0      0   100%
app/model_scripts/classifier_model.py             302    126    58%   20-28, 31-47, 93-104, 121-124, 128-167, 178, 181-185, 204, 220-225, 237-307, 329-331, 345, 348, 393-396, 411-420, 459-462, 485, 491, 505, 510, 519-520
app/model_scripts/model_loader.py                 249    144    42%   16-18, 24-26, 32-34, 40-42, 48-50, 56-58, 64-66, 95-113, 119-125, 177, 195, 202-203, 216-344, 421
app/model_scripts/ner_model.py                    161     75    53%   14-16, 44-45, 54-70, 83-103, 111-114, 120-123, 129-132, 136-156, 166-168, 180-197, 201, 224-226, 260-261
app/model_scripts/qa_model.py                     155    101    35%   47-54, 60-66, 94-127, 140-158, 168-228, 232-279, 283, 287-289
app/model_scripts/summarizer_model.py             163     75    54%   39-63, 100-105, 127-129, 139-201, 213, 218-243, 248, 266, 282, 287, 296-298, 303, 315-317, 341-353
app/model_scripts/translator_model.py             178    124    30%   41-82, 100-125, 129-160, 164-201, 207-225, 229-258, 262-264, 277-293, 298, 307-308
app/model_scripts/whisper_model.py                254    106    58%   71-81, 128-171, 196-204, 231, 246, 258, 267-320, 344-363, 384, 401-480
app/models/__init__.py                              0      0   100%
app/models/model_loader.py                         12     12     0%   2-18
app/models/notification_types.py                   61     10    84%   224-236, 251, 256, 261, 266
app/services/enhanced_notification_service.py     328    249    24%   92, 98-116, 126-148, 161-229, 238-334, 338-358, 362-418, 422-424, 442-461, 465-538, 552-568, 580-594, 612-624, 641-651, 668-678, 717-723, 741-756, 773-780, 799-807, 827-865
app/streaming/__init__.py                           3      0   100%
app/streaming/audio_buffer.py                      36      1    97%   27
app/streaming/call_session_manager.py             550    278    49%   45-47, 65, 71-78, 90-93, 121, 167-169, 220-221, 229, 237-239, 280-284, 287-288, 319-323, 335-336, 345-349, 353-354, 356-357, 360, 385-387, 391-478, 524-526, 530-636, 640-665, 669-699, 703-762, 772-787, 791-869, 920-922, 955, 959-960, 993-995, 1003, 1015-1045
app/streaming/progressive_processor.py            247     26    89%   16-18, 79, 125, 349-362, 372-374, 386-387, 441-474
app/streaming/tcp_server.py                       111     14    87%   134-160, 171-173
app/streaming/websocket_server.py                  57      0   100%
app/tasks/__init__.py                               0      0   100%
app/tasks/audio_tasks.py                          473    446     6%   28-167, 180-198, 209-379, 385-458, 474-936, 949-1004, 1010-1044, 1098-1206, 1210-1212
app/tasks/health_tasks.py                          11     11     0%   2-30
app/tasks/model_tasks.py                          300    273     9%   34-59, 65-67, 85-150, 167-270, 287-351, 369-440, 462-546, 550-586, 610-659
app/utils/__init__.py                               2      0   100%
app/utils/audio_utils.py                            0      0   100%
app/utils/mode_detector.py                         16      4    75%   16, 28-30, 38
app/utils/scp_audio_downloader.py                 232    180    22%   45, 47, 51, 100-128, 138-140, 147-158, 165-166, 179-241, 259-295, 305-312, 317-326, 338-363, 374-447, 455-475, 494-495, 499-522, 530-541, 546-555
app/utils/text_utils.py                           268    234    13%   19-20, 24, 29-33, 45-46, 53-108, 112-127, 142-180, 186, 198-199, 205-252, 256-264, 271, 286-329, 349-397, 413-475, 489-496, 511-560, 574-622
-----------------------------------------------------------------------------
TOTAL                                            7013   3843    45%
```

---
*Report generated automatically by GitHub Actions*
*Access this report at: [COVERAGE.md](https://github.com/openchlai/ai/blob/justphyl/ai_service/COVERAGE.md)*
