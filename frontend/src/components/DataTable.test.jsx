import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import DataTable from "./DataTable";
describe("DataTable", () => it("renders exactly the three Sheet headings", () => { render(<DataTable rows={[{ row: 2, A: "Apple", B: "100", C: "Mumbai" }]} />); expect(screen.getByText("Apple")).toBeTruthy(); expect(screen.getAllByRole("columnheader").map((item) => item.textContent)).toEqual(["A", "B", "C"]); }));
