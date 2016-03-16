#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""`check` command for concierge."""


import sys

import concierge.endpoints.common


class CheckApp(concierge.endpoints.common.App):

    def do(self):
        return self.output()


main = concierge.endpoints.common.main(CheckApp)

if __name__ == "__main__":
    sys.exit(main())
