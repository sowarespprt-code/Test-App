import frappe
import json
import requests


@frappe.whitelist(allow_guest=True)
def capture_agent_location(ticket_name, latitude, longitude):
    """Save agent location with human-readable address."""
    try:
        if not ticket_name:
            return {"success": False, "error": "Ticket name required"}
        if not latitude or not longitude:
            return {"success": False, "error": "Latitude and longitude required"}

        ticket = frappe.get_doc("HD Ticket", ticket_name)

        # 🔄 NEW: Save lat/lng as separate fields for frontend map**
        ticket.custom_latitude = float(latitude)
        ticket.custom_longitude = float(longitude)

        # GeoJSON for map (existing - perfect!)
        geojson = {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [float(longitude), float(latitude)]},
                "properties": {
                    "title": "Agent Start Location",
                    "agent": frappe.session.user,
                    "timestamp": frappe.utils.now()
                }
            }]
        }
        ticket.custom_location = json.dumps(geojson)

        # ✅ REVERSE GEOCODING - Get address (existing - perfect!)
        address = get_readable_address(latitude, longitude)
        ticket.custom_location_text = address
        
        ticket.save(ignore_permissions=True)
        frappe.db.commit()
        
        # 🔄 UPDATED: Return coordinates for frontend verification**
        return {
            "success": True, 
            "message": "Location saved", 
            "address": address,
            "latitude": float(latitude),
            "longitude": float(longitude)
        }
        
    except Exception as e:
        frappe.log_error(f"Location capture failed: {str(e)}", "Ticket Location Error")
        return {"success": False, "error": str(e)}

def get_readable_address(lat, lng):
    """Convert lat/lng to 'Office, Street, City, PIN' format."""
    try:
        # Nominatim (free, no API key)
        url = f"https://nominatim.openstreetmap.org/reverse"
        params = {
            'lat': lat,
            'lon': lng,
            'format': 'json',
            'addressdetails': 1,
            'zoom': 18
        }
        headers = {'User-Agent': 'FrappeHelpdesk/1.0'}
        
        response = requests.get(url, params=params, headers=headers, timeout=5)
        data = response.json()
        
        if data.get('display_name'):
            return data['display_name']
            
        # Fallback: Build from components
        address = data.get('address', {})
        parts = []
        if address.get('road'): parts.append(address['road'])
        if address.get('house_number'): parts.append(address['house_number'])
        if address.get('city_district') or address.get('city'): parts.append(address.get('city_district') or address.get('city'))
        if address.get('state_district'): parts.append(address['state_district'])
        if address.get('state'): parts.append(address['state'])
        if address.get('postcode'): parts.append(address['postcode'])
        
        return ', '.join(parts[:4]) or f"{lat:.6f}, {lng:.6f}"
        
    except:
        return f"{lat:.6f}, {lng:.6f}"
