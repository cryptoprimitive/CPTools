pragma solidity ^ 0.4.21;

contract InterfaceLog {

    event Log(uint indexed id,
              string indexed name,
              address instance,
              bytes interfaceInfo,
              string description,
              address indexed author,
              uint burned);

    uint logCount=0;

    function pushInterface(string name, address instance, bytes interfaceInfo, string description)
    payable
    external {
        emit Log(logCount, name, instance, interfaceInfo, description, msg.sender, msg.value);

        address(0x0).transfer(msg.value); // Burn ether included in call

        logCount ++;
    }
}
