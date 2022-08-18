# Main Resets script

# Imports


# API
import wikipedia as w



managers = {
      "sentences": 2,
}





# WIKIPEDIA
def search(page):

      # Search
      return w.summary(page, sentences=managers['sentences'])

