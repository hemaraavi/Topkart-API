# Topkart-API

The Topkart API is designed to handle the lightning deals functionality of the Topkart E-commerce website. It provides a set of endpoints to manage lightning deals, approve orders, and allow customers to access available deals, place orders, and check the status of their orders.

**Requirements**
To use the Topkart API, you need the following:
Python 3.x
Django framework

## API Endpoints

**User Creation**
  Endpoint: /topkart/create/users/
  Methods: POST
  Description: End point Supports creation to two types of user creation 
               1.admin
               2.customer
  Required: username(required,must be unique),password(required),email(required,must be unique),phone_number(optional),user_type(admin or customer)

**Admin Actions**
  Create and Update Lightning Deals
  Endpoint: /topkart/create/update/deals/
  Methods: POST, PUT
  Description: Admin users can create new lightning deals or update existing ones by providing the necessary data points such as product name, actual price,  final price, total units, available units,status, and expiry time. The API will validate the data and store the lightning deal in the database.

  Approve Orders or Update Orders
  Endpoint: /topkart/update/order_status/
  Methods: PUT
  Description: Admin users can approve by changing the status  orders by specifying the order ID in the request. The API will validate the order and update     its status to Approve
  Required: Order ID
  Status options: 'OPEN', 'APPROVED','CANCELLED','FULFILLED'

**Customer Actions**
  Access Available Unexpired Deals
  Endpoint: topkart/get/active/deals/
  Methods: GET
  Description: Customers can access the list of available unexpired lightning deals. The API will retrieve all deals that have not yet expired and return them   in the response, along with their data points such as product name, actual price, final price, total units, available units, and expiry time.

  Place Orders
  Endpoint: /topkart/place/order/
  Methods: POST
  Description: Customers can place orders by providing the necessary details such as the lightning deal ID, quantity, and customer ID. The API will validate     the data, check if the lightning deal is still active, and create a new order in the database.
  Required: Lightning Deal ID,Customer ID

  Check the Status of Their Order
  Endpoint: topkart/check/order_status/
  Methods: GET
  Description: Customers can check the status of their orders by specifying the order ID. The API will retrieve the order from the database and return its       current status, such as open, approved, shipped, or delivered.
  Required: Order ID
  Status options: 'OPEN', 'APPROVED','CANCELLED','FULFILLED'
                  
                 
