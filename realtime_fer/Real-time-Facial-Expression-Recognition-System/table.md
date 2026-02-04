# Training_data class counts

Source: `Training_data/` (auto-counted from folder structures and known label files).

## Notes

- ExpW counts are computed from label.lst label frequencies (not from image folders).

## Summary (dataset + split)

| Dataset | Split | Total | #Classes | Missing | Max (class=count) | MinNonZero (class=count) | Imbalance (max/min) |
|---|---:|---:|---:|---:|---:|---:|---:|
| affectnet full balanced dataset | test | 7175 | 7 | 0 | anger=1025 | anger=1025 | 1.000 |
| affectnet full balanced dataset | train | 28707 | 7 | 0 | anger=4101 | anger=4101 | 1.000 |
| Expression in-the-Wild (ExpW) Dataset | label.lst | 91793 | 7 | 0 | 6=34883 | 2=1088 | 32.062 |
| Facial Expression Image Data AFFECTNET YOLO Format | test | 2755 | 2 | 1 | images=2755 | images=2755 | 1.000 |
| Facial Expression Image Data AFFECTNET YOLO Format | train | 17101 | 2 | 1 | images=17101 | images=17101 | 1.000 |
| Facial Expression Image Data AFFECTNET YOLO Format | valid | 5406 | 2 | 1 | images=5406 | images=5406 | 1.000 |
| FER-2013 7-emotions Uniform Dataset | test | 7000 | 7 | 0 | Anger=1000 | Anger=1000 | 1.000 |
| FER-2013 7-emotions Uniform Dataset | train | 56000 | 7 | 0 | Anger=8000 | Anger=8000 | 1.000 |
| FER-2013 7-emotions Uniform Dataset | validation | 7000 | 7 | 0 | Anger=1000 | Anger=1000 | 1.000 |
| FERPlus | test | 3573 | 8 | 0 | neutral=1274 | disgust=21 | 60.667 |
| FERPlus | train | 66379 | 8 | 0 | neutral=10379 | angry=8000 | 1.297 |
| FERPlus | validation | 8341 | 8 | 0 | neutral=1341 | angry=1000 | 1.341 |

## Per-class counts

### affectnet full balanced dataset — test

| Class | Count |
|---|---:|
| anger | 1025 |
| disgust | 1025 |
| fear | 1025 |
| happy | 1025 |
| neutral | 1025 |
| sad | 1025 |
| surprise | 1025 |

### affectnet full balanced dataset — train

| Class | Count |
|---|---:|
| anger | 4101 |
| disgust | 4101 |
| fear | 4101 |
| happy | 4101 |
| neutral | 4101 |
| sad | 4101 |
| surprise | 4101 |

### Expression in-the-Wild (ExpW) Dataset — label.lst

| Class | Count |
|---|---:|
| 0 | 3671 |
| 1 | 3995 |
| 2 | 1088 |
| 3 | 30537 |
| 4 | 10559 |
| 5 | 7060 |
| 6 | 34883 |

### Facial Expression Image Data AFFECTNET YOLO Format — test

| Class | Count |
|---|---:|
| images | 2755 |
| labels | 0 |

### Facial Expression Image Data AFFECTNET YOLO Format — train

| Class | Count |
|---|---:|
| images | 17101 |
| labels | 0 |

### Facial Expression Image Data AFFECTNET YOLO Format — valid

| Class | Count |
|---|---:|
| images | 5406 |
| labels | 0 |

### FER-2013 7-emotions Uniform Dataset — test

| Class | Count |
|---|---:|
| Anger | 1000 |
| Disgust | 1000 |
| Fear | 1000 |
| Happiness | 1000 |
| Neutral | 1000 |
| Sadness | 1000 |
| Surprise | 1000 |

### FER-2013 7-emotions Uniform Dataset — train

| Class | Count |
|---|---:|
| Anger | 8000 |
| Disgust | 8000 |
| Fear | 8000 |
| Happiness | 8000 |
| Neutral | 8000 |
| Sadness | 8000 |
| Surprise | 8000 |

### FER-2013 7-emotions Uniform Dataset — validation

| Class | Count |
|---|---:|
| Anger | 1000 |
| Disgust | 1000 |
| Fear | 1000 |
| Happiness | 1000 |
| Neutral | 1000 |
| Sadness | 1000 |
| Surprise | 1000 |

### FERPlus — test

| Class | Count |
|---|---:|
| angry | 322 |
| contempt | 30 |
| disgust | 21 |
| fear | 98 |
| happy | 929 |
| neutral | 1274 |
| sad | 449 |
| suprise | 450 |

### FERPlus — train

| Class | Count |
|---|---:|
| angry | 8000 |
| contempt | 8000 |
| disgust | 8000 |
| fear | 8000 |
| happy | 8000 |
| neutral | 10379 |
| sad | 8000 |
| suprise | 8000 |

### FERPlus — validation

| Class | Count |
|---|---:|
| angry | 1000 |
| contempt | 1000 |
| disgust | 1000 |
| fear | 1000 |
| happy | 1000 |
| neutral | 1341 |
| sad | 1000 |
| suprise | 1000 |
