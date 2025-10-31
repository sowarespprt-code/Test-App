import frappe
from frappe import _
import requests

@frappe.whitelist()
def get_customer_license_details(customer_code):
    """
    Fetch customer license details from external API
    """
    try:
        # Log for debugging
        frappe.logger().info(f"Fetching license for customer code: {customer_code}")
        
        # Validate input
        if not customer_code:
            frappe.throw(_("Customer code is required"))
        
        # =================================================================
        # API Configuration - UPDATE THESE VALUES WITH YOUR ACTUAL API
        # =================================================================
        api_url = "https://your-api-url.com/api/license"  # Replace with your actual API URL
        api_key = "YOUR_API_KEY"  # Replace with your actual API key if needed
        
        # Make API call
        try:
            # Option 1: POST request (most common)
            response = requests.post(
                api_url,
                json={"customer_code": customer_code},  # Adjust payload as needed
                headers={
                    "Content-Type": "application/json",
                    # Uncomment below if your API requires authentication:
                    # "Authorization": f"Bearer {api_key}",
                    # or
                    # "X-API-Key": api_key,
                },
                timeout=10
            )
            
            # Option 2: GET request (uncomment if your API uses GET)
            # response = requests.get(
            #     f"{api_url}?customer_code={customer_code}",  # or f"{api_url}/{customer_code}"
            #     headers={
            #         "Content-Type": "application/json",
            #         # "Authorization": f"Bearer {api_key}",
            #     },
            #     timeout=10
            # )
            
            frappe.logger().info(f"API Response Status: {response.status_code}")
            frappe.logger().info(f"API Response: {response.text}")
            
            if response.status_code == 200:
                api_data = response.json()
                
                # Check if there's an error in the response
                if api_data.get("Error"):
                    frappe.throw(_("API Error: {0}").format(api_data.get("Error")))
                
                # Extract the Result object
                result = api_data.get("Result", {})
                
                if not result:
                    frappe.throw(_("No data found for customer code: {0}").format(customer_code))
                
                # Map the API response to match the expected format
                # This matches your actual API response structure
                return {
                    "CustomerCode": result.get("CustomerCode", customer_code),
                    "CustomerName": result.get("CustomerName", "").strip(),
                    "OwnerName": result.get("OwnerName", "").strip(),
                    "Address1": result.get("Address1", "").strip(),
                    "Address2": result.get("Adress2", "").strip(),  # Note: API has typo "Adress2"
                    "ContactPerson": result.get("ContactPerson", "").strip(),
                    "Phone1": result.get("Phone1", "").strip(),
                    "Phone2": result.get("Phone2", "").strip(),
                    "EmailID": result.get("EmailID", "").strip(),
                    "NatureOfBusiness": result.get("NatureOfBusiness", "").strip(),
                    "LicenseType": result.get("LicenseType", ""),
                    "SubscriptionExpDate": result.get("SubscriptionExpDate", ""),
                    "SubscriptionRemarks": result.get("SubscriptionRemarks", ""),
                    "AMCStartDate": result.get("AMCStartDate", ""),
                    "AMCEndDate": result.get("AMCEndDate", ""),
                }
            else:
                frappe.throw(_("API returned status code: {0}").format(response.status_code))
                
        except requests.exceptions.Timeout:
            frappe.log_error("API Request Timeout", "License Fetch Error")
            frappe.throw(_("Request timeout. Please try again."))
        except requests.exceptions.ConnectionError:
            frappe.log_error("API Connection Error", "License Fetch Error")
            frappe.throw(_("Could not connect to license server. Please check your internet connection."))
        except requests.exceptions.RequestException as e:
            frappe.logger().error(f"API Request Error: {str(e)}")
            frappe.throw(_("Failed to connect to license server: {0}").format(str(e)))
        
    except Exception as e:
        frappe.logger().error(f"Error in get_customer_license_details: {str(e)}")
        import traceback
        frappe.logger().error(f"Traceback: {traceback.format_exc()}")
        frappe.throw(_("Failed to fetch license details: {0}").format(str(e)))


# =================================================================
# ALTERNATIVE: If you want to get API credentials from site_config.json
# =================================================================
# Add this to your site_config.json:
# {
#     "license_api_url": "https://your-api-url.com/api/license",
#     "license_api_key": "your_actual_api_key"
# }
# 
# Then replace lines 18-19 with:
# api_url = frappe.conf.get("license_api_url")
# api_key = frappe.conf.get("license_api_key")
#
# This is more secure than hardcoding credentials


# =================================================================
# TEST FUNCTION - You can use this to test your API connection
# =================================================================
@frappe.whitelist()
def test_license_api():
    """
    Test function to check if your external API is working
    Run this from browser console:
    frappe.call({
        method: 'helpdesk.api.license.test_license_api',
        callback: function(r) { console.log(r); }
    });
    """
    try:
        api_url = "https://your-api-url.com/api/license"  # Same as above
        response = requests.get(
            api_url,
            timeout=5
        )
        return {
            "success": True,
            "status_code": response.status_code,
            "response": response.text[:500]  # First 500 chars
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }