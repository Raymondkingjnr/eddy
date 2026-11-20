export interface AuthUser {
  id: string
  email: string
  fullname: string
  is_active: boolean
  is_verified: boolean
}

export interface RegisterRequest {
  email: string
  password: string
  fullname: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface AccessTokenResponse {
  access_token: string
  token_type: string
}
