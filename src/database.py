import os
import pandas as pd

class InstagramDatabase():
    """Class to implement database for InstagramCrawler.
    """

    def __init__(self, path, file_name, columns = ["post_url", "is_post", "commenter", "text", "replies_to", "replies_count", "likes", "date", "crawl_time"]):
        self.columns = columns
        if (path == None) or (path == ""):
            raise ValueError("Path to database is not defined.")
        if (file_name == None) or (file_name == ""):
            raise ValueError("File name is not defined.")
        self.file_name = file_name
        self.path = os.path.join(path, self.file_name + ".csv")

        #create path and file if it doesnt exist
        if os.path.exists(self.path):
            self.df = pd.read_csv(self.path, low_memory=False)
        else:
            self.df = pd.DataFrame(columns=columns)

            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
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