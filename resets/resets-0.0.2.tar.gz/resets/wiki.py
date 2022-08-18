# Main Resets script

# Imports


# API
import wikipedia as w

# Manager
import manager as m





# WIKIPEDIA
def search(page):

      # Search
      return w.summary(page, sentences=m.managers['sentences'])

