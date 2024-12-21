from typing import List, Dict, Any

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from geowifi import search_networks, is_valid_bssid

app = FastAPI(
    title="GeoWiFi API",
    description="Search WiFi geolocation data by BSSID and SSID on different public databases",
    version="1.0.0"
)


class SearchRequest(BaseModel):
    identifier: str = Field(..., description="BSSID或SSID标识符")
    search_type: str = Field("bssid", description="搜索类型: 'bssid' 或 'ssid'")


class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]


@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    搜索WiFi位置信息
    
    - **identifier**: BSSID (如 "00:11:22:33:44:55") 或 SSID
    - **search_type**: "bssid" 或 "ssid"
    """
    try:
        # 验证搜索类型
        if request.search_type not in ["bssid", "ssid"]:
            raise HTTPException(status_code=400, detail="搜索类型必须是 'bssid' 或 'ssid'")

        # 如果是BSSID搜索，验证格式
        if request.search_type == "bssid":
            if not is_valid_bssid(request.identifier):
                raise HTTPException(status_code=400, detail="无效的BSSID格式")
            results = search_networks(bssid=request.identifier)
        else:
            results = search_networks(ssid=request.identifier)

        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
