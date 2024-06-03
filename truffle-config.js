module.exports = {
  networks: {
    development: {
      host: "127.0.0.1",
      port: 8545,
      network_id: "*", // Match any network id
    },
  },
  compilers: {
    solc: {
      version: "0.8.21", // Solidity derleyici sürümü
      settings: {
        optimizer: {
          enabled: true,
          runs: 200,
        },
        evmVersion: "byzantium", // EVM versiyonunu belirtebilirsiniz
      },
    },
  },
  mocha: {
    reporter: "eth-gas-reporter",
    reporterOptions: {
      currency: "USD",
      gasPrice: 1,
    },
  },
};
