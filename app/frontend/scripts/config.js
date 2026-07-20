// Change this to your laptop's IP when testing on tablet
// Use 'localhost' when testing on the laptop browser

export const SHOP_ID = "HM1"

export const API_BASE = window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : `http://${window.location.hostname}:8000`;