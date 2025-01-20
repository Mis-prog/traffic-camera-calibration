import numpy as np
from dataclasses import dataclass
import cv2

@dataclass
class TrafficSign:
    """Class representing a traffic sign in the scene"""
    x: float  # x coordinate in image
    y: float  # y coordinate in image
    height: float  # height in pixels
    real_size: float  # real size in meters
    elevation: float  # height above ground in meters
    angle: float  # in-plane rotation angle

class SceneCalibration:
    def __init__(self, image_path: str):
        """Initialize calibration with image"""
        self.image = cv2.imread(image_path)
        self.signs = []
        self.k = None  # projection parameter
        self.ground_plane = None

    def add_traffic_sign(self, x: float, y: float, height: float, 
                        real_size: float, elevation: float, angle: float):
        """Add detected traffic sign to the scene"""
        sign = TrafficSign(x, y, height, real_size, elevation, angle)
        self.signs.append(sign)

    def calculate_spherical_image_height(self, sign: TrafficSign, k: float) -> float:
        """Calculate height of spherical image for given sign"""
        y_top = sign.y - sign.height/2
        y_bottom = sign.y + sign.height/2
        
        h_spherical = k * abs(
            np.arctan(y_top/k) - np.arctan(y_bottom/k)
        )
        return h_spherical

    def calculate_map_scale(self, sign: TrafficSign, k: float) -> float:
        """Calculate map scale for given sign"""
        h_spherical = self.calculate_spherical_image_height(sign, k)
        return sign.real_size / h_spherical

    def calculate_3d_coordinates(self, k: float) -> np.ndarray:
        """Calculate 3D coordinates of all signs for given k"""
        coordinates = []
        
        for sign in self.signs:
            # Calculate vector to planar image
            v_planar = np.array([sign.x, sign.y, k])
            
            # Normalize to spherical image
            v_spherical = k * v_planar / np.linalg.norm(v_planar)
            
            # Calculate scale and real coordinates
            scale = self.calculate_map_scale(sign, k)
            v_real = v_spherical * scale
            
            # Calculate foot point (projection to ground)
            foot_shift = np.array([
                np.sin(sign.angle) * sign.elevation,
                np.cos(sign.angle) * sign.elevation,
                0
            ])
            foot_point = v_real - foot_shift
            
            coordinates.append(foot_point)
            
        return np.array(coordinates)

    def calculate_plane_error(self, k: float) -> float:
        """Calculate error for fitting points to a plane for given k"""
        points = self.calculate_3d_coordinates(k)
        
        # Center the points
        centroid = np.mean(points, axis=0)
        centered_points = points - centroid
        
        # Calculate covariance matrix
        cov_matrix = np.dot(centered_points.T, centered_points)
        
        # Get eigenvalues
        eigenvalues = np.linalg.eigvals(cov_matrix)
        
        # Smallest eigenvalue represents the error
        return min(eigenvalues)

    def find_optimal_k(self, k_min: float = 0.001, k_max: float = 0.1, 
                      steps: int = 1000) -> float:
        """Find optimal projection parameter k"""
        k_values = np.logspace(np.log10(k_min), np.log10(k_max), steps)
        errors = [self.calculate_plane_error(k) for k in k_values]
        
        optimal_k_idx = np.argmin(errors)
        self.k = k_values[optimal_k_idx]
        return self.k

    def calibrate(self):
        """Perform full calibration of the scene"""
        if len(self.signs) < 4:
            raise ValueError("Need at least 4 traffic signs for calibration")
            
        # Find optimal k
        optimal_k = self.find_optimal_k()
        
        # Calculate final 3D coordinates
        points = self.calculate_3d_coordinates(optimal_k)
        
        # Calculate ground plane parameters
        centroid = np.mean(points, axis=0)
        centered_points = points - centroid
        
        # PCA to find plane normal
        cov_matrix = np.dot(centered_points.T, centered_points)
        eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)
        
        # Normal vector is eigenvector with smallest eigenvalue
        normal = eigenvectors[:, 0]
        
        self.ground_plane = {
            'normal': normal,
            'point': centroid
        }
        
        return {
            'projection_parameter': optimal_k,
            'ground_plane': self.ground_plane,
            'points': points
        }

    def measure_distance(self, x1: float, y1: float, x2: float, y2: float) -> float:
        """Measure real-world distance between two points on calibrated image"""
        if self.k is None:
            raise ValueError("Scene must be calibrated first")
            
        # Convert image coordinates to 3D points
        point1 = self.project_to_ground_plane(x1, y1)
        point2 = self.project_to_ground_plane(x2, y2)
        
        # Calculate Euclidean distance
        return np.linalg.norm(point1 - point2)

    def project_to_ground_plane(self, x: float, y: float) -> np.ndarray:
        """Project image point to ground plane"""
        if self.ground_plane is None:
            raise ValueError("Scene must be calibrated first")
            
        # Create ray from camera center through image point
        ray_dir = np.array([x, y, self.k])
        ray_dir = ray_dir / np.linalg.norm(ray_dir)
        
        # Intersect ray with ground plane
        normal = self.ground_plane['normal']
        point = self.ground_plane['point']
        
        t = np.dot(point - np.array([0, 0, 0]), normal) / np.dot(ray_dir, normal)
        intersection = t * ray_dir
        
        return intersection