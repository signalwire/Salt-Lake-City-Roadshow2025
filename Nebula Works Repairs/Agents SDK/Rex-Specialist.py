#!/usr/bin/env python3
"""
Rex - Technical Specialist Agent for Nebula Works Repairs
This agent handles technical diagnostics and troubleshooting for spacecraft repairs.
"""

from signalwire_agents import AgentBase, SwaigFunctionResult


class RexSpecialistAgent(AgentBase):
    def __init__(self):
        # Configuration values
        agent_name = "Rex Technical Specialist"
        route = "/rex"
        host = "0.0.0.0"
        port = 5001
        basic_auth = ("username", "password")

        super().__init__(
            name=agent_name,
            route=route,
            host=host,
            port=port,
            basic_auth=basic_auth
        )

        # Print the full authenticated URL (use localhost for display when host is 0.0.0.0)
        display_host = "localhost" if host == "0.0.0.0" else host
        auth_url = f"http://{basic_auth[0]}:{basic_auth[1]}@{display_host}:{port}{route}"
        print(f"\n{'='*60}")
        print(f"Rex Specialist Agent URL: {auth_url}")
        print(f"{'='*60}\n")

        # Configure the main prompt with variable substitution for transferred parameters
        self.set_prompt_text("""You are Rex, the senior technical specialist at Nebula Works Repairs.

This call was transferred from ${from_agent}.

Start by saying: "Hi! I'm Rex, your technical specialist. I understand you're having issues with ${customer_problem|problem_description}. Let me help you with ${customer_problem|problem_description}"

Your job is to:
1. Repeat the ${customer_problem} back to the customer is a compassionate way. Ask clarifying questions about the ${customer_problem}
2. Diagnose the issue thoroughly
3. Once diagnosis is complete, use transfer_back function to send them to Nova for scheduling

You are an expert in:
- Hyperdrive systems
- Navigation computers
- Engine diagnostics
- Shield generators
- Life support systems

Always provide clear diagnosis before transferring back.""")

        # Configure language and voice (Rex uses a different voice)
        self.add_language(
            code="en-US",
            name="English",
            voice="rime.orion",
            engine="rime",
            model="arcana"
        )

        # Set AI parameters
        self.set_params({
            "end_of_speech_timeout": 2500,
            "attention_timeout": 30000,
            "inactivity_timeout": 60000,
            "swaig_allow_swml": True,
            "debug_webhook_url": "https://webhook.site/77bdecb9-3993-497a-b111-ac2940157ed5",
            "debug_webhook_level": 10,
            "video_idle_file": "https://www.dropbox.com/scl/fi/ayin4h0zc8d3r7ha47un0/rex-still.mp4?rlkey=971qh9tn96pcu1ejmo0fxw7bz&st=gtkdpy3h&dl=1",
            "video_talking_file": "https://www.dropbox.com/scl/fi/hbxfomvjz6ymz0mnlqfcq/0_1080_N.mp4?rlkey=kqbee2qqbzq0hw5vybt6yt9pa&st=bnac40qg&dl=1"
        })

        # Set initial global data for incoming transfer parameters
        # These would be set from the incoming request parameters
        self.set_global_data({
            "customer_problem": "${params.problem_description}",
            "from_agent": "${params.transferred_from|receptionist}"
        })

        # Define SWAIG functions
        self._define_functions()

    def _define_functions(self):
        """Define all SWAIG functions for Rex"""

        # Run diagnostics function
        @self.tool()
        def run_diagnostics(system: str, symptoms: str):
            """
            Run diagnostic tests on spacecraft systems

            Args:
                system: Which system to diagnose (hyperdrive, navigation, engine, shields, life_support)
                symptoms: Detailed symptoms the customer described
            """
            result = SwaigFunctionResult()
            result.set_response(
                f"Diagnostics complete. Found issue with {system}. "
                f"Repair needed: {symptoms} indicates component failure. "
                f"Estimated repair time: 2-3 hours."
            )
            return result.to_json()

        # Transfer back to receptionist function
        @self.tool()
        def transfer_back(diagnosis: str, repair_time: str):
            """
            Return caller to receptionist for scheduling after diagnosis

            Args:
                diagnosis: Complete diagnosis results and repair recommendations
                repair_time: Estimated repair time
            """
            result = SwaigFunctionResult()

            # Add say action first
            result.add_action({
                "say": "Thanks for explaining the issue. I've completed the diagnosis. Let me transfer you back to Nova to schedule your repair."
            })

            # Add SWML connect action with all the transfer parameters
            result.add_action({
                "SWML": {
                    "version": "1.0.0",
                    "sections": {
                        "main": [
                            {
                                "connect": {
                                    "to": "https://demo.signalwire.com/relay-bins/3517ad6d-1c3f-42f4-960d-eac399a1e5a5",
                                    "headers": {
                                        "tech_notes": f"${{args.diagnosis}}",
                                        "repair_time": f"${{args.repair_time}}",
                                        "problem_description": "${customer_problem}",
                                        "transferred_from": "Rex",
                                        "diagnosis_complete": "true"
                                    }
                                }
                            }
                        ]
                    }
                }
            })

            # Add stop action
            result.add_action({
                "stop": "true"
            })

            result.set_response("transferred back to receptionist, the call has ended.")
            return result.to_json()


if __name__ == "__main__":
    # Create and run the agent
    agent = RexSpecialistAgent()
    agent.run()
