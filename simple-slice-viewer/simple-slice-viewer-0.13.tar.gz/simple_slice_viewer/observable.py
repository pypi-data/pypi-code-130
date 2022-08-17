from simple_slice_viewer.logger import Logger

LOG_LEVEL = Logger.LEVEL_DEBUG
# -*- coding: utf-8 -*-

class Observable(Logger):
    """
    Superclass to generate events that can be observed externally.
    Used for a Model, View, Controller (MVC) GUI design
    """
    def __init__(self, log_level=LOG_LEVEL):
        super().__init__(log_level=log_level)
        self.callbacks = {}

    def subscribe(self, subscriber, event_name, callback):
        """
        Add a listener for a specific event.

        Parameters
        ----------
        subscriber : Object
            Object that listens for event.
        event_name : string
            Name of event that is listent to.
        callback : function
            Function that is called when event is fired/generated.
            A single positional argument is passed that contais specific data
            for the event.

        Returns
        -------
        None.

        """
        if subscriber not in self.callbacks.keys():
            self.callbacks[subscriber] = {}
        
        self.callbacks[subscriber][event_name] = [True, callback]

    def unsubscribe(self, subscriber, event_name=None):
        """
        Remove a specific listener/subscriber

        Parameters
        ----------
        subscriber : Object
            Object that listens for event.
        event_name : string, optional
            DIf specified only a specific event is removed for this subscriber.
            If None all events are unsubscribed. The default is None.

        Returns
        -------
        None.

        """
        if subscriber in self.callbacks:
            if event_name is None:
                self.callbacks.pop(subscriber)
            elif event_name in self.callbacks[subscriber]:
                self.callbacks[subscriber].pop(event_name)
                if len(self.callbacks[subscriber]) == 0:
                    self.callbacks.pop(subscriber)

    def disable_subscription(self, subscriber, event_name=None):
        """
        Disable a subscriber for events (temporarily).

        Parameters
        ----------
        subscriber : Object
            Object that listens for event.
        event_name : string, optional
            DIf specified only a specific event is disabled for this subscriber.
            If None all events are disabled. The default is None.

        Returns
        -------
        None.

        """
        if event_name:
            self.callbacks[subscriber][event_name][0] = False
        else:
            for event_name in self.calbacks[subscriber].keys():
                self.callbacks[subscriber][event_name][0] = False


    def enable_subscription(self, subscriber, event_name=None):
        """
        Enable a subscriber for events (temporarily).

        Parameters
        ----------
        subscriber : Object
            Object that listens for event.
        event_name : string, optional
            DIf specified only a specific event is enabled for this subscriber.
            If None all events are enabled. The default is None.

        Returns
        -------
        None.

        """

        if event_name:
            self.callbacks[subscriber][event_name][0] = True
        else:
            for event_name in self.calbacks[subscriber].keys():
                self.callbacks[subscriber][event_name][0] = True


    def fire(self, event_name, event_data=None):
        """
        Generate/Fire an event

        Parameters
        ----------
        event_name : string
            Name of the event that is generated/fired.
        event_data : Object, optional
            Event data that is passed to subscribers/listeners.
            The default is None.

        Returns
        -------
        None.

        """
        self.logger.debug(f'Fire {event_name}')
        for subscriber, events in self.callbacks.items():
            if event_name in events.keys():
                self.logger.debug(f'Object of type: {type(subscriber)} is subscribed to event!')
                enabled, callback = self.callbacks[subscriber][event_name]
                if enabled:
                    self.logger.debug(f'Calling subscriber callback! {callback}')
                    callback(event_data)
                else:
                    self.logger.debug('Subscriber disabled not fired!')