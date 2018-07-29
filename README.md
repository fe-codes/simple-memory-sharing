# simple-memory-sharing
An easy way to cache data in the memory and share between processes.

By using this file you can easily cache data in the memory and share them between different processes even on different hosts.
To the simplest way, you only need to implement the fetch_data(key) function which determines how the data  associated with the key is generated . For example, you can pass a image file path as the key, open the file and do some preprocess such as resizing and return the preprocessed data.  For a client to get the data, just pass the file path and the data will be returned.
