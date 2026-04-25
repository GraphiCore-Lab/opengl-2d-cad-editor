"""
Base shape interface - tüm shape'ler bunu extends eder.
Kişi 2 bu dosyayı kullanarak line/rect/circle yazar.
Kişi 1 transform matrislerini buraya uygular.
"""
import numpy as np


class BaseShape:
    def __init__(self):
        self.color = (1.0, 1.0, 1.0)       # RGB, 0.0-1.0 arası
        self.fill = True                     # True=dolu, False=sadece kenar
        self.line_width = 2.0
        self.selected = False
        # 3x3 transform matrisi (2D homogeneous)
        self.transform = np.identity(3, dtype=float)

    def draw(self):
        """OpenGL ile shape'i çiz. Alt sınıf override eder."""
        raise NotImplementedError

    def contains(self, x, y):
        """Verilen nokta bu shape'in içinde mi? Hit-test için."""
        raise NotImplementedError

    def get_bounds(self):
        """(x, y, width, height) döndür. Selection box için."""
        raise NotImplementedError

    def apply_transform(self, matrix):
        """Dışarıdan verilen 3x3 matrisi mevcut transform'a uygula."""
        self.transform = matrix @ self.transform

    def get_transformed_point(self, x, y):
        """Bir noktayı mevcut transform ile dönüştür."""
        p = np.array([x, y, 1.0])
        result = self.transform @ p
        return result[0], result[1]

    def to_dict(self):
        """JSON kayıt için dict döndür. Alt sınıf override eder."""
        return {
            "type": self.__class__.__name__,
            "color": list(self.color),
            "fill": self.fill,
            "line_width": self.line_width,
            "transform": self.transform.tolist(),
        }

    @classmethod
    def from_dict(cls, data):
        """JSON'dan shape yükle. Alt sınıf override eder."""
        raise NotImplementedError