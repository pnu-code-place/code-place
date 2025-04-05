"""
GitHub OAuth authentication server.

This module provides endpoints for retrieving GitHub personal access tokens
through the OAuth flow.
"""
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx

from .config import settings

app = FastAPI()


class TokenRequest(BaseModel):
    """Request model for token issuance."""
    code: str


class TokenResponse(BaseModel):
    """Response model containing the issued access token."""
    access_token: str


async def exchange_code_for_token(code: str) -> Dict[str, Any]:
    """
    Exchange OAuth code for a GitHub access token.
    
    Args:
        code: The temporary OAuth code from GitHub.
        
    Returns:
        Dict containing the response from GitHub, including access_token.
        
    Raises:
        HTTPException: If the GitHub API request fails.
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(settings.ACCESS_TOKEN_URL,
                                     headers={"Accept": "application/json"},
                                     data={
                                         "client_id": settings.GITHUB_OAUTH_APP_ID,
                                         "client_secret": settings.GITHUB_OAUTH_APP_SECRET,
                                         "code": code,
                                     })

        data = response.json()
        if response.status_code != 200:
            error_message = data.get('error_description', 'Unknown error')
            raise HTTPException(status_code=400, detail=f"Failed to get access token: {error_message}")

        return data


@app.post("/token/issue", response_model=TokenResponse)
async def issue_access_token(request: TokenRequest) -> TokenResponse:
    """
    Issue a personal access token (PAT) for GitHub.
    
    Args:
        request: The request object containing the OAuth code.
        
    Returns:
        A TokenResponse containing the GitHub access token.
        
    Raises:
        HTTPException: If token issuance fails.
    """
    try:
        token_data = await exchange_code_for_token(request.code)
        return TokenResponse(access_token=token_data["access_token"])
    except HTTPException:
        # Re-raise HTTP exceptions without modification
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
