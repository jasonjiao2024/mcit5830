// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

contract Source is AccessControl {
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant WARDEN_ROLE = keccak256("BRIDGE_WARDEN_ROLE");
    
    mapping(address => bool) public approved;
    address[] public tokens;
    
    // CRITICAL: Must have 4 parameters including 'sender'
    event Deposit(
        address indexed token,
        address indexed sender,
        address indexed recipient,
        uint256 amount
    );
    
    event Withdrawal(
        address indexed token,
        address indexed recipient,
        uint256 amount
    );
    
    event Registration(address indexed token);
    
    constructor(address admin) {
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(ADMIN_ROLE, admin);
        _grantRole(WARDEN_ROLE, admin);
    }
    
    function deposit(address _token, address _recipient, uint256 _amount) public {
        require(approved[_token], "Token not registered");
        require(_amount > 0, "Invalid amount");
        require(_recipient != address(0), "Invalid recipient");
        require(ERC20(_token).transferFrom(msg.sender, address(this), _amount), "Transfer failed");
        
        // CRITICAL: Emit with msg.sender as the 'sender' parameter
        emit Deposit(_token, msg.sender, _recipient, _amount);
    }
    
    function withdraw(address _token, address _recipient, uint256 _amount) 
        public onlyRole(WARDEN_ROLE) {
        require(_recipient != address(0), "Invalid recipient");
        require(_amount > 0, "Invalid amount");
        require(ERC20(_token).transfer(_recipient, _amount), "Transfer failed");
        
        emit Withdrawal(_token, _recipient, _amount);
    }
    
    function registerToken(address _token) public onlyRole(ADMIN_ROLE) {
        require(_token != address(0), "Invalid token");
        require(!approved[_token], "Already registered");
        approved[_token] = true;
        tokens.push(_token);
        
        emit Registration(_token);
    }
}
