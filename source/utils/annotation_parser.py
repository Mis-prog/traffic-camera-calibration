import json
from collections import defaultdict

class AnnotationParser:
    def __init__(self, filepath):
        self.filepath = filepath
        self.annotations = {"lines": {}, "points": {}}
        self._load()

    def _load(self):
        with open(self.filepath, "r", encoding="utf-8") as f:
            self.annotations = json.load(f)
            # Убедимся, что оба типа присутствуют
            self.annotations.setdefault("lines", {})
            self.annotations.setdefault("points", {})

    def get_all_classes(self):
        classes = set(self.annotations["lines"].keys()) | set(self.annotations["points"].keys())
        return sorted(classes)

    def get_points_by_class(self, class_name):
        return self.annotations["points"].get(class_name, [])

    def get_lines_by_class(self, class_name):
        return self.annotations["lines"].get(class_name, [])

    def get_all_points(self):
        all_points = []
        for cls, pts in self.annotations["points"].items():
            all_points.extend(pts)
        return all_points

    def get_all_lines(self):
        all_lines = []
        for cls, lines in self.annotations["lines"].items():
            all_lines.extend(lines)
        return all_lines

    def count_per_class(self):
        stats = {}
        for cls in self.get_all_classes():
            stats[cls] = {
                "points": len(self.get_points_by_class(cls)),
                "lines": len(self.get_lines_by_class(cls))
            }
        return stats

if __name__ == "__main__":
    parser = AnnotationParser("../../example/karls_marks/marked/data_full.json")

    print("Классы:", parser.get_all_classes())
    print("Точек всего:", len(parser.get_all_points()))
    print("Линий всего:", len(parser.get_all_lines()))

    stats = parser.count_per_class()
    for cls, s in stats.items():
        print(f"{cls}: {s['points']} точек, {s['lines']} линий")