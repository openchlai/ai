# 📊 Code Coverage Report - AI Service

**Branch:** 267/merge
**Commit:** [\`857396c\`](https://github.com/openchlai/ai/commit/857396c06e4b253a1409196c9ca0544681b97e34)
**Generated:** 2025-08-15 12:55:19 UTC
**Python Version:** 3.12
**Workflow:** [\`16990295220\`](https://github.com/openchlai/ai/actions/runs/16990295220)

## 🎯 Coverage Summary

![Coverage](https://img.shields.io/badge/Coverage-48%25-orange)

| Metric | Value | Status |
|--------|-------|--------|
| **Coverage** | 48% | ❌ Fail |
| **Threshold** | 80% | Target |

## 📈 Detailed Coverage Report

```
Name                                         Stmts   Miss  Cover   Missing
--------------------------------------------------------------------------
app/__init__.py                                  1      0   100%
app/api/__init__.py                              0      0   100%
app/api/audio_routes.py                        277    192    31%   44, 111, 116, 149-151, 190, 198-200, 205-230, 235-240, 245-304, 313-341, 356-554, 572-668
app/api/call_session_routes.py                 223     65    71%   14-15, 117, 130-134, 145, 170-174, 182, 193, 210-237, 247, 251, 262, 273, 281-291, 296-306, 319-321, 327, 334, 349, 361, 381-389, 400-410
app/api/classifier_route.py                     49      6    88%   46, 79, 91, 99-106
app/api/health_routes.py                       101     43    57%   49-50, 119, 126-195, 218-240
app/api/ner_routes.py                           54      2    96%   52, 97
app/api/qa_route.py                             47     19    60%   36-71, 80-84, 89-101
app/api/summarizer_routes.py                    48      0   100%
app/api/translator_routes.py                    42      0   100%
app/api/whisper_routes.py                       65      4    94%   46, 75, 130, 153
app/celery_app.py                               10      1    90%   7
app/config/__init__.py                           0      0   100%
app/config/settings.py                          73     13    82%   97, 105-119
app/core/__init__.py                             0      0   100%
app/core/celery_monitor.py                      61     42    31%   21-93, 97, 106, 114
app/core/resource_manager.py                   118     25    79%   88-89, 134-135, 150-151, 166-167, 197, 201-206, 210-228, 235-239
app/core/streaming.py                          106     80    25%   22-29, 33-40, 44, 56-86, 96, 118, 141-143, 160, 175, 193-261, 265-283, 287-294
app/core/text_chunker.py                       156     26    83%   70-72, 77-79, 86-90, 98, 158-182, 290
app/main.py                                    112     69    38%   36-99, 132, 137-140, 149, 178-199, 214-217, 221-242
app/model_scripts/__init__.py                    7      0   100%
app/model_scripts/classifier_model.py          221     68    69%   21-29, 32-48, 86, 107-110, 120, 125, 149-153, 171, 188-193, 200-241, 265-268, 279, 282, 337-340, 355, 370, 385, 390, 397
app/model_scripts/model_loader.py              203    122    40%   15-17, 23-25, 31-33, 39-41, 47-49, 55-57, 63-65, 127, 145, 152-153, 159-162, 166-273, 277-290, 294-299, 324, 329, 334, 339, 344, 350
app/model_scripts/ner_model.py                  74     15    80%   32-34, 41-43, 50, 59-63, 107-109
app/model_scripts/qa_model.py                  132     85    36%   52-56, 62-68, 101-118, 138-198, 215-240, 258-312, 317, 321-323
app/model_scripts/summarizer_model.py          160     68    58%   36, 43, 73-77, 108-113, 135-137, 147-209, 221, 226-251, 256, 274, 290, 295, 304-306, 311, 323-325
app/model_scripts/translator_model.py          149     91    39%   40, 77-102, 106-130, 134-171, 177-195, 199-228, 232-234, 247-263, 268, 277-278
app/model_scripts/whisper_model.py             146     19    87%   77-78, 131, 165-181, 211, 228, 246, 250-251, 269-273, 294
app/models/__init__.py                           0      0   100%
app/models/model_loader.py                      12     12     0%   2-18
app/services/agent_notification_service.py     192    104    46%   70-71, 90-115, 138-139, 144, 148-150, 154-160, 175-225, 242-251, 256-266, 271-286, 291-304, 309-320, 337-346, 350-358, 363-373, 379-388, 392-418, 428-457, 461-470
app/streaming/__init__.py                        3      0   100%
app/streaming/audio_buffer.py                   34      4    88%   48-51
app/streaming/call_session_manager.py          509    374    27%   20-22, 39-42, 47-49, 91-92, 100-102, 107-175, 179-206, 214-219, 246-250, 256-257, 262, 266-269, 282-283, 296-298, 302-346, 350-453, 457-479, 483-513, 517-576, 586-601, 605-683, 687, 691-695, 714-734, 747-760, 767, 771-772, 776-790, 810-821, 832-880, 884-967, 971-1000
app/streaming/progressive_processor.py         245    188    23%   15-17, 33-35, 50-52, 70-92, 97-140, 145-190, 194-204, 209-245, 257-293, 298-312, 321-363, 368-393, 397-410, 414-422, 427-463, 467
app/streaming/tcp_server.py                    101     25    75%   55, 88-90, 101-104, 117-118, 147-148, 152-165, 169-173, 179
app/streaming/websocket_server.py               57     41    28%   22-75, 79-101, 105
app/tasks/__init__.py                            0      0   100%
app/tasks/audio_tasks.py                       408    380     7%   24-48, 55-194, 200, 207-225, 236-290, 306-778, 791-846, 852-863, 915-1006
--------------------------------------------------------------------------
TOTAL                                         4196   2183    48%
```

---
*Report generated automatically by GitHub Actions*
*Access this report at: [COVERAGE.md](https://github.com/openchlai/ai/blob/267/merge/ai_service/COVERAGE.md)*
