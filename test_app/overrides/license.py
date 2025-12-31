import frappe
from frappe import _
import requests
import json

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

        api_customer_code = customer_code.split('_')[0] if '_' in customer_code else customer_code
        
        frappe.logger().info(f"Original customer code: {customer_code}, API customer code: {api_customer_code}")
        
        # API Configuration
        api_url = "http://licmanager.soware.in/api/LicCustomer/uspGetCustomerDetails"
        
        # Make API call
        try:
            # POST request with customer code
            response = requests.post(
                api_url,
                json={"CustomerCode": api_customer_code},
                headers={
                    "Content-Type": "application/json",
                },
                timeout=10
            )
            
            frappe.logger().info(f"API Response Status: {response.status_code}")
            frappe.logger().info(f"API Response Text: {response.text}")
            
            if response.status_code == 200:
                api_data = response.json()
                frappe.logger().info(f"API Response JSON: {json.dumps(api_data, indent=2)}")
                
                # Check if there's an error in the response
                if api_data.get("Error"):
                    frappe.throw(_("API Error: {0}").format(api_data.get("Error")))
                
                # Extract the Result object
                result = api_data.get("Result", {})
                
                if not result:
                    frappe.throw(_("No data found for customer code: {0}").format(api_customer_code))
                
                # Clean up the data (remove leading/trailing spaces)
                cleaned_data = {
                    "CustomerCode": str(result.get("CustomerCode", api_customer_code)).strip(),
                    "CustomerName": str(result.get("CustomerName", "")).strip(),
                    "OwnerName": str(result.get("OwnerName", "")).strip(),
                    "Address1": str(result.get("Address1", "")).strip(),
                    "Address2": str(result.get("Adress2", "")).strip(),  # Note: API has typo
                    "ContactPerson": str(result.get("ContactPerson", "")).strip(),
                    "Phone1": str(result.get("Phone1", "")).strip(),
                    "Phone2": str(result.get("Phone2", "")).strip(),
                    "EmailID": str(result.get("EmailID", "")).strip(),
                    "NatureOfBusiness": str(result.get("NatureOfBusiness", "")).strip(),
                    "LicenseType": str(result.get("LicenseType", "")).strip(),
                    "LicKey": str(result.get("LicKey", "")).strip(),  # Added LicKey field
                    "SubscriptionExpDate": str(result.get("SubscriptionExpDate", "")).strip(),
                    "SubscriptionRemarks": str(result.get("SubscriptionRemarks", "")).strip(),
                    "AMCStartDate": str(result.get("AMCStartDate", "")).strip(),
                    "AMCEndDate": str(result.get("AMCEndDate", "")).strip(),
                }
                
                frappe.logger().info(f"Cleaned data being returned: {json.dumps(cleaned_data, indent=2)}")
                return cleaned_data
                
            elif response.status_code == 404:
                frappe.throw(_("Customer not found with code: {0}").format(customer_code))
            else:
                frappe.throw(_("API returned status code: {0}. Response: {1}").format(
                    response.status_code, 
                    response.text[:200]
                ))
                
        except requests.exceptions.Timeout:
            frappe.log_error("API Request Timeout", "License Fetch Error")
            frappe.throw(_("Request timeout. Please try again."))
        except requests.exceptions.ConnectionError as e:
            frappe.log_error(f"API Connection Error: {str(e)}", "License Fetch Error")
            frappe.throw(_("Could not connect to license server. Please check your internet connection."))
        except requests.exceptions.RequestException as e:
            frappe.logger().error(f"API Request Error: {str(e)}")
            frappe.log_error(f"API Request Error: {str(e)}", "License Fetch Error")
            frappe.throw(_("Failed to connect to license server: {0}").format(str(e)))
        except json.JSONDecodeError as e:
            frappe.logger().error(f"JSON Decode Error: {str(e)}")
            frappe.log_error(f"Invalid JSON response: {response.text}", "License Fetch Error")
            frappe.throw(_("Received invalid response from server"))
        
    except Exception as e:
        frappe.logger().error(f"Error in get_customer_license_details: {str(e)}")
        import traceback
        frappe.logger().error(f"Traceback: {traceback.format_exc()}")
        frappe.log_error(traceback.format_exc(), "License Fetch Error")
        frappe.throw(_("Failed to fetch license details: {0}").format(str(e)))


@frappe.whitelist()
def test_license_api(customer_code="CU065641980"):
    """
    Test function to check API response
    Run from browser console:
    frappe.call({
        method: 'helpdesk.api.license.test_license_api',
        args: {customer_code: 'CU065641980'},
        callback: function(r) { console.log(r.message); }
    });
    """
    try:
        api_customer_code = customer_code.split('_')[0] if '_' in customer_code else customer_code

        api_url = "http://licmanager.soware.in/api/LicCustomer/uspGetCustomerDetails"
        
        response = requests.post(
            api_url,
            json={"CustomerCode": api_customer_code},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        result = {
            "success": True,
            "status_code": response.status_code,
            "response_text": response.text,
            "response_json": response.json() if response.status_code == 200 else None
        }
        
        # Log LicKey if present
        if response.status_code == 200:
            json_data = response.json()
            if json_data.get("Result"):
                lic_key = json_data["Result"].get("LicKey")
                frappe.logger().info(f"LicKey found: {lic_key}")
                result["lic_key"] = lic_key
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "original_code": customer_code,
            "api_code_used": api_customer_code if 'api_customer_code' in locals() else None,
            "error": str(e)
        }

