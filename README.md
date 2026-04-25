# OpenGL 2D CAD — BIL333 Final Project

## Kurulum
```bash
pip install -r requirements.txt
python main.py
```

## Klasör Yapısı
```
main.py                  ← buradan çalıştır
src/
  app.py                 ← Pygame pencere + ana döngü       (Kişi 3)
  renderer.py            ← OpenGL render                    (Kişi 1)
  input_handler.py       ← Mouse/klavye olayları            (Kişi 3)
  core/
    scene.py             ← Shape listesi, seçim, undo/redo  (Kişi 1)
    transform.py         ← 2D matrix işlemleri              (Kişi 1)
  shapes/
    base.py              ← Ortak interface                   (ORTAK)
    line.py              ← Çizgi                            (Kişi 2)
    rectangle.py         ← Dikdörtgen                       (Kişi 2)
    circle.py            ← Daire                            (Kişi 2)
  utils/
    constants.py         ← Tüm sabitler                     (ORTAK)
    file_ops.py          ← Save / Load JSON                 (Kişi 3)
```

## Branch Planı
| Branch | Kişi | Ne yapıyor |
|---|---|---|
| `feature/core-engine` | Kişi 1 | scene.py, transform.py, renderer.py |
| `feature/shapes` | Kişi 2 | line, rect, circle + transformlar |
| `feature/ui-and-input` | Kişi 3 | app.py, input_handler, toolbar, file_ops |

## Kontroller (şimdilik)
| Tuş | İşlev |
|---|---|
| `Delete` | Seçili sil |
| `Ctrl+Z` | Geri al |
| `Ctrl+Y` | İleri al |
| `Ctrl+D` | Kopyala |
| `Ctrl+S` | Kaydet (scene.json) |
| `Ctrl+O` | Yükle (scene.json) |

## Tool Değiştirme (InputHandler üzerinden)
```python
input_handler.current_tool = TOOL_LINE    # çizgi
input_handler.current_tool = TOOL_RECT    # dikdörtgen
input_handler.current_tool = TOOL_CIRCLE  # daire
input_handler.current_tool = TOOL_SELECT  # seç
input_handler.current_tool = TOOL_MOVE    # taşı
```