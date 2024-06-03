// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ContentRegistry {
    struct Content {
        string id;
        string title;
        string author;
        string date;
        string content;
        string contentHash;
        address authorAddress;
        uint256 timestamp;
        bool verified;
    }

    mapping(string => Content) public contents;
    event ContentAdded(string id, string title, string author, string date, string content, string contentHash);

    function registerContent(
        string memory _id,
        string memory _title,
        string memory _author,
        string memory _date,
        string memory _content,
        string memory _contentHash
    ) public {
        contents[_id] = Content({
            id: _id,
            title: _title,
            author: _author,
            date: _date,
            content: _content,
            contentHash: _contentHash,
            authorAddress: msg.sender,
            timestamp: block.timestamp,
            verified: false
        });

        emit ContentAdded(_id, _title, _author, _date, _content, _contentHash);
    }

    function getContent(string memory _id) public view returns (Content memory) {
        return contents[_id];
    }
}
