# 📊 Code Coverage Report - AI Service

**Branch:** 403/merge
**Commit:** [\`a957a08\`](https://github.com/openchlai/ai/commit/a957a089582c5462e8533199b177d52c8df79e1e)
**Generated:** 2025-10-09 07:08:39 UTC
**Python Version:** 3.12
**Workflow:** [\`18368193502\`](https://github.com/openchlai/ai/actions/runs/18368193502)

## 🎯 Coverage Summary

![Coverage](https://img.shields.io/badge/Coverage-47%25-orange)

| Metric | Value | Status |
|--------|-------|--------|
| **Coverage** | 47% | ❌ Fail |
| **Threshold** | 80% | Target |

## 📈 Detailed Coverage Report

```
Name                                         Stmts   Miss  Cover   Missing
--------------------------------------------------------------------------
app/__init__.py                                  1      0   100%
app/api/__init__.py                              0      0   100%
app/api/audio_routes.py                        277    192    31%   44, 111, 116, 149-151, 190, 198-200, 205-230, 235-240, 245-304, 313-341, 356-554, 572-668
app/api/call_session_routes.py                 223     65    71%   14-15, 117, 130-134, 145, 170-174, 182, 193, 210-237, 247, 251, 262, 273, 281-291, 296-306, 319-321, 327, 334, 349, 361, 381-389, 400-410
app/api/classifier_route.py                    100     29    71%   71, 114-199, 244, 256, 264-271
app/api/feedback_routes.py                     100     45    55%   134-182, 194-258, 270-288, 299
app/api/health_routes.py                       101     43    57%   49-50, 119, 126-195, 218-240
app/api/ner_routes.py                           72     11    85%   52, 75-99, 144
app/api/notification_routes.py                  93     65    30%   30-38, 43-73, 78-97, 102-127, 132-141, 146-202, 207-251
app/api/processing_mode_routes.py               93     63    32%   32-41, 46-59, 64-92, 97-120, 125-144, 149-184, 188-194
app/api/qa_route.py                            133     98    26%   41-69, 74-116, 125-243, 251-255, 260-272, 277-302
app/api/summarizer_routes.py                    66      8    88%   73-90
app/api/translator_routes.py                    58      9    84%   66-81
app/api/whisper_model_routes.py                104     75    28%   30-38, 43-57, 62-85, 90-109, 114-132, 137-176, 181-213
app/api/whisper_routes.py                       65      4    94%   46, 75, 130, 153
app/celery_app.py                               10      1    90%   7
app/config/__init__.py                           0      0   100%
app/config/settings.py                         200     46    77%   182-187, 191-206, 211, 219-221, 232-237, 248-254, 258, 301-307, 337, 345-358
app/core/__init__.py                             0      0   100%
app/core/celery_monitor.py                      61     42    31%   21-93, 97, 106, 114
app/core/notification_manager.py               169    117    31%   57-60, 76-78, 91-128, 132-138, 142-152, 156-160, 164-170, 189-210, 214-230, 236-287, 291-300, 304, 319-325
app/core/processing_modes.py                    93     25    73%   106, 116-150, 154
app/core/processing_strategy_manager.py        124     48    61%   95-97, 120-131, 140-143, 153, 160, 168, 195-210, 268, 298-332
app/core/resource_manager.py                   118     25    79%   88-89, 134-135, 150-151, 166-167, 197, 201-206, 210-228, 235-239
app/core/streaming.py                          106     80    25%   22-29, 33-40, 44, 56-86, 96, 118, 141-143, 160, 175, 193-261, 265-283, 287-294
app/core/text_chunker.py                       156     26    83%   70-72, 77-79, 86-90, 98, 158-182, 290
app/core/whisper_model_manager.py              217    167    23%   57-61, 67-71, 75-76, 80-87, 91, 95, 99-108, 128-171, 185-223, 227-247, 251-268, 272, 279, 283-288, 292, 317-357, 361-376, 380, 418-454
app/main.py                                    116     69    41%   36-99, 136, 141-144, 153, 188-209, 224-227, 231-252
app/model_scripts/__init__.py                    7      0   100%
app/model_scripts/audio_processing.py            0      0   100%
app/model_scripts/classifier_model.py          247     83    66%   21-29, 32-48, 96-107, 125-128, 147, 172-176, 188, 191, 195, 198-202, 215, 232-237, 244-285, 309-312, 323, 326, 381-384, 399, 414, 429, 434, 441
app/model_scripts/model_loader.py              222    141    36%   15-17, 23-25, 31-33, 39-41, 47-49, 55-57, 63-65, 131, 149, 156-157, 163-166, 170-301, 305-318, 322-327, 352, 357, 362, 367, 372, 378
app/model_scripts/ner_model.py                 152     64    58%   14-16, 44-45, 53-65, 87-93, 103-106, 112-115, 121-124, 128-148, 158-160, 172-189, 193, 216-218
app/model_scripts/qa_model.py                  160     97    39%   50-52, 58-64, 106-123, 140-158, 168-228, 232-254, 261-308, 312, 316-318
app/model_scripts/summarizer_model.py          157     67    57%   38, 60-64, 95-100, 122-124, 134-196, 208, 213-238, 243, 261, 277, 282, 291-293, 298, 310-312
app/model_scripts/translator_model.py          172    102    41%   40, 48-52, 55-56, 68-69, 95-120, 124-155, 159-196, 202-220, 224-253, 257-259, 272-288, 293, 302-303
app/model_scripts/whisper_model.py             319    164    49%   31-36, 87-97, 140-181, 204-212, 239, 253, 256, 261, 265-268, 280, 289-342, 366-385, 408, 423, 428-509, 544-581, 598-613, 647-689
app/models/__init__.py                           0      0   100%
app/models/model_loader.py                      12     12     0%   2-18
app/services/agent_notification_service.py     198    137    31%   56-63, 70-71, 75-120, 124-144, 148-150, 154-160, 166-225, 229-237, 242-251, 256-266, 271-286, 291-304, 309-320, 324-333, 337-346, 350-358, 362-370, 375-385, 390-400, 406-415, 419-445, 455-484, 488-497
app/streaming/__init__.py                        3      0   100%
app/streaming/audio_buffer.py                   36      1    97%   27
app/streaming/call_session_manager.py          634    376    41%   23-25, 54, 69, 104, 143-145, 182-215, 260-264, 267-268, 299-303, 316-317, 327-328, 333-335, 338, 342-350, 370-455, 501-503, 507-613, 617-639, 643-673, 677-736, 746-761, 765-843, 894-896, 929, 933-934, 976-1006, 1010-1044, 1048-1096, 1100-1184, 1188-1217, 1221-1261
app/streaming/progressive_processor.py         245     10    96%   15-17, 78, 124, 361-363, 375-376
app/streaming/tcp_server.py                    109     11    90%   133-159
app/streaming/websocket_server.py               57      0   100%
app/tasks/__init__.py                            0      0   100%
app/tasks/audio_tasks.py                       492    461     6%   24-48, 55-194, 207-225, 236-290, 306-855, 868-923, 929-940, 992-1115, 1130-1252
app/utils/__init__.py                            2      0   100%
app/utils/audio_utils.py                         0      0   100%
app/utils/scp_audio_downloader.py              172    132    23%   31-32, 89-117, 127-129, 136-147, 154-155, 168-230, 248-284, 294-301, 308-350, 369-390, 398-409, 414-423
app/utils/text_utils.py                        230    193    16%   29-33, 53-108, 112-127, 142-180, 186, 205-252, 256-264, 271, 286-329, 349-397, 412-447, 455-503
--------------------------------------------------------------------------
TOTAL                                         6482   3404    47%
```

---
*Report generated automatically by GitHub Actions*
*Access this report at: [COVERAGE.md](https://github.com/openchlai/ai/blob/403/merge/ai_service/COVERAGE.md)*
