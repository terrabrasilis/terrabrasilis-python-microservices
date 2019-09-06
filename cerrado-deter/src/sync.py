#!/usr/bin/python3
from copy_service import CopyService
from intersection_service import IntersectionService

"""
Running daily with cron job to copy data and process intersections.
"""
copyService = CopyService()
copyService.copyData()

intersectionService = IntersectionService()
intersectionService.execIntersections()