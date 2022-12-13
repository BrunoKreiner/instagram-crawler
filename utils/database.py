import os
import pandas as pd

class InstagramDatabase():
    """Class to implement database for InstagramCrawler.
    """

    def __init__(self, path, columns = ["post_url", "is_post", "commenter", "text", "replies_to", "replies_count", "likes", "date", "crawl_time"]):
        self.columns = columns
        self.path = path

        if os.path.exists(path):
            # File with
            self.df = pd.read_csv(path, low_memory=False)
        else:
            self.df = pd.DataFrame(columns=columns)
            self.save_db_state()

    def get_entry(self, idx):
        """_summary_

        Args:
            id (string or int): Index of the entry to retrieve

        Returns:
            _type_: _description_
        """
        return self.df.iloc[idx]

    def add_entry(self, post_uuid, post_entry):
        """Adds a new entry to the database.

        Args:
            post_uuid (string): Unique identifier for the entry.
            post_entry (pandas.Series object): Entry to add to the database.
        """
        self.df.loc[post_uuid] = post_entry
    
    def delete_entry(self, id):
        raise NotImplementedError()

    def update_entry(self, id, content):
        raise NotImplementedError()

    def save_db_state(self):
        self.df.to_csv(self.path)