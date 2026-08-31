"""
Pydantic 响应模型
"""
from pydantic import BaseModel
from typing import Optional, List


class MarketOverview(BaseModel):
    total_sales: int
    brand_count: int
    model_count: int
    new_energy_penetration: float
    avg_price: float
    avg_rating: float


class BrandRanking(BaseModel):
    brand_name: str
    brand_category: str
    brand_country: str
    total_sales: int
    market_share: float


class BrandCategory(BaseModel):
    brand_category: str
    total_sales: int
    model_count: int
    market_share: float


class PriceDistribution(BaseModel):
    price_range: str
    model_count: int
    percentage: float


class PriceSales(BaseModel):
    price_range: str
    total_sales: int
    model_count: int
    market_share: float


class EnergyTypeSales(BaseModel):
    energy_type: str
    total_sales: int
    model_count: int
    market_share: float


class PenetrationTrend(BaseModel):
    year_month: str
    new_energy_sales: int
    total_sales: int
    penetration_rate: float


class RatingDistribution(BaseModel):
    rating_range: str
    model_count: int
    percentage: float


class BrandRating(BaseModel):
    brand_name: str
    brand_category: str
    overall_score: float
    appearance_score: float
    interior_score: float
    power_score: float
    space_score: float
    fuel_score: float
    handling_score: float
    comfort_score: float
    value_score: float
    model_count: int


class ModelRating(BaseModel):
    model_name: str
    brand_name: str
    energy_type: str
    price: float
    overall_score: float
    review_count: int


class MonthlySales(BaseModel):
    year_month: str
    total_sales: int


class YoYGrowth(BaseModel):
    brand_name: str
    current_sales: int
    last_sales: int
    yoy_growth: float


class CitySales(BaseModel):
    city: str
    province: str
    region: str
    sales_volume: int


class RegionSales(BaseModel):
    region: str
    sales_volume: int
