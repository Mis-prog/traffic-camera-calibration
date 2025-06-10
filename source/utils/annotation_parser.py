import json
from collections import defaultdict

class AnnotationParser:
    def __init__(self, filepath):
        self.filepath = filepath
        self.annotations = {"line": {}, "point": {}}
        self._load()

    def _load(self):
        with open(self.filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.annotations["point"] = data.get("point", {})
        self.annotations["line"] = data.get("line", {})

    def get_all_classes(self):
        return sorted(set(self.annotations["point"]) | set(self.annotations["line"]))

    def get_points_by_class(self, class_name):
        return [ann["image"] for ann in self.annotations["point"].get(class_name, []) if "image" in ann]

    def get_lines_by_class(self, class_name):
        return [ann["image"] for ann in self.annotations["line"].get(class_name, []) if "image" in ann]

    def get_all_points(self):
        points = []
        for ann_list in self.annotations["point"].values():
            points.extend([ann["image"] for ann in ann_list if "image" in ann])
        return points

    def get_all_lines(self):
        lines = []
        for ann_list in self.annotations["line"].values():
            lines.extend([ann["image"] for ann in ann_list if "image" in ann])
        return lines

    def count_per_class(self):
        stats = {}
        for cls in self.get_all_classes():
            stats[cls] = {
                "point": len(self.annotations["point"].get(cls, [])),
                "line": len(self.annotations["line"].get(cls, [])),
            }
        return stats

    def get_gps_points_by_class(self, class_name):
        return [ann["gps"] for ann in self.annotations["point"].get(class_name, []) if "gps" in ann]

    def get_gps_lines_by_class(self, class_name):
        return [ann["gps"] for ann in self.annotations["line"].get(class_name, []) if "gps" in ann]

if __name__ == "__main__":
    parser = AnnotationParser("../../example/karls_marks/data/data_full.json")

    print("Классы:", parser.get_all_classes())
    print("Точек всего:", len(parser.get_all_points()))
    print("Линий всего:", len(parser.get_all_lines()))

    for cls, s in parser.count_per_class().items():
        print(f"{cls}: {s['point']} точек, {s['line']} линий")
