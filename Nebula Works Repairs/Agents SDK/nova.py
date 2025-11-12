#!/usr/bin/env python3
"""
Nova - Receptionist Agent for Nebula Works Repairs
This agent handles initial customer inquiries and transfers technical issues to specialists.
"""

from signalwire_agents import AgentBase, SwaigFunctionResult


class NovaAgent(AgentBase):
    def __init__(self):
        # Configuration values
        agent_name = "Nova Receptionist"
        route = "/nova"
        host = "0.0.0.0"
        port = 5000
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
        print(f"Nova Agent URL: {auth_url}")
        print(f"{'='*60}\n")

        # Configure the main prompt
        self.set_prompt_text("""## Identity
You are Nova, the receptionist for Nebula Works Repairs.

## Greeting
Start every conversation by saying: 'Hello! This is Nova from Nebula Works Repairs. How can I help you today?'

## Capabilities
You can handle the following types of inquiries:

### Business Hours
Provide information about when we're open.
- We're open Monday through Saturday
- Operating hours: 8am to 8pm
- Closed on Sundays

### Pricing Information
Answer questions about repair costs.
- Repairs typically cost between 1000 and 5000 credits
- Exact pricing depends on the specific repair needed

### General Questions
Handle all other non-technical inquiries about our services.

## Transfer Rules
When to transfer to a technical specialist:
- For TECHNICAL problems like engine issues
- For hyperdrive problems
- For any complex spacecraft repair questions
- Use the transfer_to_specialist function when transferring

## Communication Guidelines
How to interact with customers:
- Be friendly and professional
- Listen carefully to understand if the issue is technical
- When transferring, say: 'I am going to transfer you to one of our technical specialists to help get your rocket flying again.'""")

        # Configure language and voice
        self.add_language(
            code="en-US",
            name="English",
            voice="rime.astra",
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
            "video_idle_file": "https://www.dropbox.com/scl/fi/5jfokiizzew2k6d0b58fx/nova_still.mov?rlkey=dt45psrxoefjv95hkbp2i8hmf&st=zmcbzor3&dl=1",
            "video_talking_file": "https://www.dropbox.com/scl/fi/4iwb485ubysqeb4vo7ypz/1_1080_N-1.mp4?rlkey=h1rnk3nwv3f63a16bnlkcv9u9&st=epsjco0s&dl=1"
        })

        # Set post prompt URL
        self.set_post_prompt_url("https://webhook.site/77bdecb9-3993-497a-b111-ac2940157ed5")

        # Define SWAIG functions
        self._define_functions()

    def _define_functions(self):
        """Define all SWAIG functions for Nova"""

        # Check hours function
        @self.tool()
        def check_hours():
            """
            Tell customer our business hours
            """
            result = SwaigFunctionResult()
            result.set_response("We're open Monday through Saturday, 8am to 8pm. Closed Sundays.")
            return result.to_json()

        # Transfer to specialist function
        @self.tool()
        def transfer_to_specialist(problem: str):
            """
            Transfer technical problems to our specialist

            Args:
                problem: What technical issue they have
            """
            result = SwaigFunctionResult()
            result.set_response("Transferring to specialist now.")

            # Add say action
            result.add_action({
                "say": "I am going to transfer you to one of our technical specialists to help get your rocket flying again."
            })

            # Add SWML transfer action
            result.add_action({
                "SWML": {
                    "version": "1.0.0",
                    "sections": {
                        "main": [
                            {
                                "transfer": {
                                    "dest": "https://demo.signalwire.com/relay-bins/c976efbe-cf2d-475d-9831-f7b1fa74a0ee",
                                    "params": {
                                        "problem_description": f"${{args.problem}}",
                                        "transferred_from": "Nova",
                                        "transfer_time": "${time.now}"
                                    }
                                }
                            }
                        ]
                    }
                }
            })

            return result.to_json()


if __name__ == "__main__":
    # Create and run the agent
    agent = NovaAgent()
    agent.run()
