from app.db import SessionLocal
from app.orm_models import LibraryVersion, Section, Bullet

def seed():
    with SessionLocal() as s:
        v1 = LibraryVersion(version_label = "v1", is_active=True)
        s.add(v1)
        s.flush()

        sec_i = Section(library_version_id=v1.id, code="I",organization = "N/A", title="General Information", introduction="A general introduction of who I am and what I do", order=1)
        sec_a = Section(library_version_id=v1.id, code="A",organization = "Administrative Office of the Courts - KY", title="Applications Development Officer", introduction="A brief introduction of what I do as the appdev officer", order=2)
        sec_b = Section(library_version_id=v1.id, code="B",organization = "BrickBridge Consulting LLC",title="Founder/Product Manager", introduction="A brief introduction of what I do as the appdev officer", order=3)
        sec_c = Section(library_version_id=v1.id, code="C",organization = "Navigate Enterprise Center", title="Director", introduction="A brief introduction of what I do as the appdev officer", order=4)
        s.add_all([sec_i, sec_a,sec_b,sec_c])
        s.flush()

        s.add_all(
            [
                Bullet(section_id=sec_a.id, text="Provided project leadership on $37 million modernization initiative to transition core applications—including the eFiling and Court Case Management systems—to a commercial off-the-shelf (COTS) solution from Tyler Technologies."),
                Bullet(section_id=sec_a.id, text="Rearchitected the KYeCourts system and developed 87 new applications, databases, and services to support the COTS solution."),
                Bullet(section_id=sec_a.id, text="Fostered executive and stakeholder engagement via daily standups, steering committee briefs, and weekly agile reporting."),
                Bullet(section_id=sec_a.id, text="Built governance frameworks to manage project risks, develop risk mitigation strategies, ensure accountability, and drive progress across internal teams and vendor partnerships."),
                Bullet(section_id=sec_a.id, text="Drove developer productivity gains by embedding AI-enabled workflows and agile practices into SDLC modernization initiatives."),
                Bullet(section_id=sec_a.id, text="Led CI/CD implementation with Azure DevOps pipelines to accelerate secure, production-grade deployments."),
                Bullet(section_id=sec_a.id, text="Established tooling—including Playwright, GitHub Actions, code coverage tracking—to support AI-assisted quality assurance."),
                Bullet(section_id=sec_a.id, text="Modernized engineering workflows with AI integrations, Azure DevOps and GitHub, driving GitOps, YAML pipelines, and integrated backlog management."),
                Bullet(section_id=sec_a.id, text="Led ITIL-aligned change management under PMO governance, tracking environment deltas, issuing change notices, and delivering weekly release reports for cross-team and leadership alignment."),
                Bullet(section_id=sec_a.id, text="Led high-velocity dev engagements and cross-functional planning for enterprise-scale rollouts aligned with critical delivery timelines."),
                Bullet(section_id=sec_a.id, text="Organized process improvement through Agile workflow rearchitecture, increasing story velocity by 30% and reducing cycle time by 40% across delivery teams."),
                Bullet(section_id=sec_a.id, text="Introduced AI-aligned developer KPIs and tooling benchmarks to quantify productivity, adoption, and performance impact."),
                Bullet(section_id=sec_a.id, text="Engaged enterprise stakeholders to align DevSecOps strategy and drive adoption of new developer tooling and cloud architecture."),
                Bullet(section_id=sec_a.id, text="Achieved 19% Azure cost savings via service optimization and vendor consolidation; identified tech stack synergies to reduce licensed software spend by 10%."),
                Bullet(section_id=sec_a.id, text="Led problem remediation initiatives within the ITIL framework, exceeding service availability standards through performance dashboards and rapid issue resolution."),
                Bullet(section_id=sec_a.id, text="Coordination with INFOSEC to ensure all applications adhered to KCOJ standards, including broad adoption of CIS IG1."),
                Bullet(section_id=sec_a.id, text="Used Launch Darkly to A/B test dev builds with whitelisted user groups, gathering feedback to improve product delivery."),
                Bullet(section_id=sec_a.id, text="Tested feature hypotheses using Launch Darkly A/B builds; iterated based on KPI-aligned user feedback loops"),
                Bullet(section_id=sec_a.id, text="Partnered with users and design teams to refine UI via continuous feedback loops, optimizing UX journeys and informing iterative product improvements."),
                Bullet(section_id=sec_b.id, text="Negotiated a 3-year, $500K contract to design and develop a cloud-based software application to modernize the Homeownership Readiness industry white labeled under the client’s brand. Founded Brick Bridge Consulting and filled key technical positions to meet definitions of done in the project management plan."),
                Bullet(section_id=sec_b.id, text="Partnered with sales in pre-sales engagements to showcase product capabilities; led discovery sessions, crafted mockups, and delivered live demos of prototypes and MVPs to drive client buy-in."),
                Bullet(section_id=sec_b.id, text="Owned the product design process from end-to-end beginning with requirement discovery through product launch. Drafted low-fidelity wireframes and database schemas."),
                Bullet(section_id=sec_b.id, text="Voice of the Customer and lead weekly product demonstration meetings with key stakeholders to collect feedback and iterate on the strategic product roadmap."),
                Bullet(section_id=sec_b.id, text="Collaborated with multiple cross-functional teams including backend, UI/UX, Marketing &amp Documentation. Owned and prioritized the product backlog and led scrum ceremonies."),
                Bullet(section_id=sec_b.id, text="Architected cloud-native APIs on AWS for secure platform integration, with containerized services and automated scaling."),
                Bullet(section_id=sec_b.id, text="Championed customer feedback loops and stakeholder alignment to iteratively evolve roadmap and accelerate product-market fit."),
                Bullet(section_id=sec_b.id, text="Led end-to-end product design lifecycle—from discovery to launch—prioritizing user needs, usability, and market-fit outcomes."),
                Bullet(section_id=sec_c.id, text="Raised $1.2M over two years through grant funding to support operations and an excess of 170 clients seeking support in launching, expanding, or recovering a small business."),
                Bullet(section_id=sec_c.id, text="Raised a $500K direct micro-loan portfolio to provide capital to start-up Louisville micro-enterprises. Managed loan servicing, collections, and technical assistance."),
                Bullet(section_id=sec_c.id, text="Groomed some dogs"),
            
            
            
            ]
        )
        s.commit()

if __name__ == "__main__":
    seed()