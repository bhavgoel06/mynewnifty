from breeze_connect import BreezeConnect

class BreezeAPIWrapper:
    """A wrapper class for the ICICI Breeze API."""

    def __init__(self, api_key, api_secret):
        """
        Initializes the BreezeAPIWrapper.

        Args:
            api_key (str): Your Breeze API key.
            api_secret (str): Your Breeze API secret.
        """
        self.breeze = BreezeConnect(api_key=api_key)
        self.api_key = api_key
        self.api_secret = api_secret
        self.ws_connected = False

    def connect(self, session_token):
        """
        Generates a session using the provided session token.

        Args:
            session_token (str): The session token obtained after login.
        """
        try:
            self.breeze.generate_session(api_secret=self.api_secret, session_token=session_token)
            print("Successfully generated session.")
            return True
        except Exception as e:
            print(f"Failed to generate session: {e}")
            return False

    def connect_websocket(self, on_ticks_callback):
        """
        Connects to the WebSocket and sets up a tick listener.

        Args:
            on_ticks_callback (function): The function to call when a tick is received.
        """
        if not self.ws_connected:
            try:
                self.breeze.ws_connect()
                self.breeze.on_ticks = on_ticks_callback
                self.ws_connected = True
                print("WebSocket connected successfully.")
            except Exception as e:
                print(f"Failed to connect to WebSocket: {e}")
        else:
            print("WebSocket is already connected.")

    def disconnect_websocket(self):
        """Disconnects from the WebSocket."""
        if self.ws_connected:
            self.breeze.ws_disconnect()
            self.ws_connected = False
            print("WebSocket disconnected.")

    def subscribe_feeds(self, **kwargs):
        """Subscribes to feeds for a given instrument."""
        return self.breeze.subscribe_feeds(**kwargs)

    def unsubscribe_feeds(self, **kwargs):
        """Unsubscribes from feeds for a given instrument."""
        return self.breeze.unsubscribe_feeds(**kwargs)

    def get_historical_data(self, **kwargs):
        """Gets historical data for a given instrument."""
        return self.breeze.get_historical_data(**kwargs)

    def get_option_chain_quotes(self, **kwargs):
        """Gets option chain quotes."""
        return self.breeze.get_option_chain_quotes(**kwargs)

    def get_quotes(self, **kwargs):
        """Gets quotes for a given instrument."""
        return self.breeze.get_quotes(**kwargs)

    def place_order(self, **kwargs):
        """Places an order."""
        return self.breeze.place_order(**kwargs)

    def get_order_details(self, **kwargs):
        """Gets details for a specific order."""
        return self.breeze.get_order_detail(**kwargs)

    def get_order_list(self, **kwargs):
        """Gets a list of orders."""
        return self.breeze.get_order_list(**kwargs)

    def cancel_order(self, **kwargs):
        """Cancels an order."""
        return self.breeze.cancel_order(**kwargs)

    def modify_order(self, **kwargs):
        """Modifies an order."""
        return self.breeze.modify_order(**kwargs)

    def get_portfolio_positions(self):
        """Gets portfolio positions."""
        return self.breeze.get_portfolio_positions()

    def get_portfolio_holdings(self, **kwargs):
        """Get portfolio holdings."""
        return self.breeze.get_portfolio_holdings(**kwargs)

    def get_funds(self):
        """Get funds."""
        return self.breeze.get_funds()
