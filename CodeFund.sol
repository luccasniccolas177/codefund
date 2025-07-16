// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// --- Contrato Campaign (Actualizado) ---
contract Campaign {
    struct Milestone {
        string description;
        uint256 amount;
        string verificationUrl; // URL (ej. GitHub PR) para la verificación automática.
        bool verified;
        bool fundsReleased;
    }

    address public immutable developer;
    string public name;
    string public description;
    string public githubUrl; // URL del repositorio principal del proyecto.
    uint256 public immutable fundingGoal;
    uint256 public immutable deadline;
    uint256 public totalRaised;
    uint256 public contributorCount;
    mapping(address => uint256) public contributions;
    Milestone[] public milestones;

    event Contribution(address indexed contributor, uint256 amount);
    event MilestoneCreated(uint256 indexed milestoneId, string description);
    event MilestoneApproved(uint256 indexed milestoneId, address indexed approver);
    event FundsReleased(uint256 indexed milestoneId, uint256 amount);

    modifier onlyDeveloper() {
        require(msg.sender == developer, "Campaign: Caller is not the developer");
        _;
    }

    // --- CONSTRUCTOR ACTUALIZADO ---
    constructor(
        string memory _name,
        string memory _description,
        string memory _githubUrl,
        uint256 _fundingGoal,
        uint256 _deadline,
        address _developer,
        string[] memory _milestoneDescriptions,
        uint256[] memory _milestoneAmounts,
        string[] memory _milestoneUrls
    ) {
        require(_fundingGoal > 0, "Goal must be positive");
        require(_milestoneDescriptions.length == _milestoneAmounts.length && _milestoneDescriptions.length == _milestoneUrls.length, "Mismatched milestone data");

        name = _name;
        description = _description;
        githubUrl = _githubUrl;
        fundingGoal = _fundingGoal;
        deadline = _deadline;
        developer = _developer;

        for (uint i = 0; i < _milestoneDescriptions.length; i++) {
            milestones.push(Milestone({
                description: _milestoneDescriptions[i],
                amount: _milestoneAmounts[i],
                verificationUrl: _milestoneUrls[i],
                verified: false,
                fundsReleased: false
            }));
        }
    }

    function contribute() public payable {
        require(block.timestamp < deadline, "Deadline has passed");
        contributions[msg.sender] += msg.value;
        totalRaised += msg.value;
        emit Contribution(msg.sender, msg.value);
    }

    // `approveMilestone` ahora puede ser llamado por cualquier dirección (el agente),
    // pero la lógica de quién puede llamar se gestionará off-chain o con roles futuros.
    function approveMilestone(uint256 _milestoneId) public {
        Milestone storage milestone = milestones[_milestoneId];
        require(!milestone.verified, "Milestone already verified");
        milestone.verified = true;
        emit MilestoneApproved(_milestoneId, msg.sender);
    }

    function releaseMilestoneFunds(uint256 _milestoneId) public onlyDeveloper {
        Milestone storage milestone = milestones[_milestoneId];
        require(milestone.verified, "Milestone not verified");
        require(!milestone.fundsReleased, "Funds already released");
        require(address(this).balance >= milestone.amount, "Insufficient balance");
        milestone.fundsReleased = true;
        payable(developer).transfer(milestone.amount);
        emit FundsReleased(_milestoneId, milestone.amount);
    }
    
    // Funciones de vista (getters) no necesitan cambios significativos para esta fase.
    function getCampaignDetails() public view returns (string memory, string memory, string memory, uint256, uint256, uint256, address) {
        return (name, description, githubUrl, fundingGoal, deadline, totalRaised, developer);
    }
    function getMilestones() public view returns (Milestone[] memory) { return milestones; }
}

// --- Contrato CampaignFactory (Actualizado) ---
contract CampaignFactory {
    address[] public deployedCampaigns;
    event CampaignCreated(address indexed campaignAddress, address indexed developer, string name);

    function createCampaign(
        string memory _name,
        string memory _description,
        string memory _githubUrl,
        uint256 _fundingGoal,
        uint256 _deadline,
        string[] memory _milestoneDescriptions,
        uint256[] memory _milestoneAmounts,
        string[] memory _milestoneUrls
    ) public {
        Campaign newCampaign = new Campaign(
            _name, _description, _githubUrl, _fundingGoal, _deadline, msg.sender,
            _milestoneDescriptions, _milestoneAmounts, _milestoneUrls
        );
        deployedCampaigns.push(address(newCampaign));
        emit CampaignCreated(address(newCampaign), msg.sender, _name);
    }
    function getDeployedCampaigns() public view returns (address[] memory) { return deployedCampaigns; }
}
